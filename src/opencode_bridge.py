"""
OpenAI-compatible bridge in front of the local OpenCode agent.

Exposes:
  GET  /v1/models
  POST /v1/chat/completions   {model, messages, max_tokens?, temperature?}

Each call becomes one stateless `opencode run` in an empty sandbox directory
(so the agent cannot touch the research workspace). Requires working opencode
auth (`opencode auth login`) — until then calls fail exactly as `opencode run`
fails (currently provider 401s).

Run: .venv/bin/uvicorn src.opencode_bridge:app --port 8378
"""
import asyncio
import json
import os
import subprocess
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SANDBOX = Path(os.environ.get("OPENCODE_SANDBOX", "/tmp/opencode/sandbox"))
SANDBOX.mkdir(parents=True, exist_ok=True)
CALL_TIMEOUT = int(os.environ.get("OPENCODE_TIMEOUT", "300"))

# /tmp can be wiped (reboot/cleaner), silently dropping the reasoning config.
# Re-create it whenever missing so max-reasoning is never accidentally off.
_SANDBOX_CONFIG = {
    "$schema": "https://opencode.ai/config.json",
    "provider": {"opencode": {"models": {
        "muse-spark-1.3-contributor-free": {"name": "Muse Spark 1.3", "reasoning": True},
        "muse-spark-1.3-contributor-free#xhigh": {"name": "Muse Spark 1.3 xhigh", "reasoning": True},
        "mimo-v2.6-flash-free": {"name": "Mimo v2.6", "reasoning": True},
        "space-bunny-free": {"name": "Space Bunny", "reasoning": True},
    }}},
}
_cfg = SANDBOX / "opencode.json"
if not _cfg.exists():
    _cfg.write_text(json.dumps(_SANDBOX_CONFIG, indent=2))

def _opencode_bin() -> str:
    import shutil
    checked = []
    explicit = os.environ.get("OPENCODE_BIN")
    if explicit:
        checked.append(f"OPENCODE_BIN={explicit} exists={Path(explicit).exists()}")
        if Path(explicit).exists():
            return explicit
    found = shutil.which("opencode")
    checked.append(f"PATH-> {found or 'miss'}")
    if found:
        return found
    # The server may run as a different user (e.g. root) whose $HOME lacks the
    # binary — also check the project owner's home explicitly.
    for home in dict.fromkeys([str(Path.home()), "/home/karan"]):
        cand = str(Path(home) / ".opencode" / "bin" / "opencode")
        exists = Path(cand).exists()
        checked.append(f"HOME={home} exists={exists}")
        if exists:
            return cand
    raise HTTPException(500, "opencode binary not found [" + " | ".join(checked) + "]")

# Full gateway-style IDs stay intact here (no CrewAI routing to strip them).
BRIDGE_MODELS = [
    {"id": "opencode/mimo-v2.6", "opencode": "opencode/mimo-v2.6-flash-free",
     "label": "Mimo v2.6", "hint": "via OpenCode · max reasoning"},
]

app = FastAPI(title="OpenCode bridge (OpenAI-compatible)")


class ChatIn(BaseModel):
    model: str
    messages: list
    max_tokens: int | None = None
    temperature: float | None = None
    tools: list | None = None
    tool_choice: object | None = None


def _resolve(model: str) -> str:
    for m in BRIDGE_MODELS:
        if model in (m["id"], m["opencode"]):
            return m["opencode"]
    # passthrough: lets callers address any `provider/model` opencode knows
    return model


def _prompt(messages: list, tools: list | None = None) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
        if role == "tool":
            parts.append(f"[helper result]\n{content}")
            continue
        # surface prior assistant tool calls so the loop stays coherent
        tcs = m.get("tool_calls") or []
        for tc in tcs:
            fn = (tc.get("function") or {})
            parts.append(f"[you called {fn.get('name')} with {fn.get('arguments')}]")
        if content:
            parts.append(f"[{role}]\n{content}")
    base = ("Reason thoroughly before answering. Answer concisely (at most 80 words), as plain text. "
            "Do not edit files or run commands on your computer.")
    if tools:
        descs = []
        for t in tools:
            fn = t.get("function", {}) if isinstance(t, dict) else {}
            descs.append(f"- {fn.get('name')}: {fn.get('description', '')} "
                         f"Parameters: {json.dumps(fn.get('parameters', {}))[:600]}")
        base += ("\n\nYou have helper functions. When you need one, reply with ONLY this JSON on one line "
                 "and nothing else: {\"call\": \"<helper-name>\", \"args\": {<parameter values>}}. "
                 "Call at most one helper per reply. When you have what you need, answer normally.\n"
                 "Helpers:\n" + "\n".join(descs))
    return base + "\n\n" + "\n\n".join(parts)


def _extract_call(text: str):
    """Find {"call": name, "args": {...}} in model text. Returns (name, args_dict) or None.
    Uses balanced-brace scanning so nested args objects parse."""
    import re
    for m in re.finditer(r'"call"\s*:\s*"([^"]+)"', text):
        # walk back to the enclosing opening brace
        start = text.rfind("{", 0, m.start())
        if start < 0:
            continue
        depth, i, in_str, esc = 0, start, False, False
        end = -1
        while i < len(text):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            i += 1
        if end < 0:
            continue
        try:
            obj = json.loads(text[start:end])
        except json.JSONDecodeError:
            continue
        if isinstance(obj.get("call"), str):
            args = obj.get("args", {})
            return obj["call"], args if isinstance(args, dict) else {}
    return None


def _run_opencode_sync(model: str, prompt: str) -> str:
    cmd = [_opencode_bin(), "run", prompt, "-m", model, "--format", "json"]
    try:
        proc = subprocess.run(cmd, cwd=SANDBOX, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"opencode run timed out after {CALL_TIMEOUT}s")
    texts = []
    err = None
    for line in (proc.stdout or "").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "error":
            err = ev.get("error", {})
        part = ev.get("part", {}) or {}
        if part.get("type") == "text" and part.get("text"):
            texts.append(part["text"])
    if err:
        raise HTTPException(502, f"opencode provider error: {json.dumps(err)[:300]}")
    out = "".join(texts).strip()
    if not out:
        raise HTTPException(502, f"opencode returned no text (exit={proc.returncode}, stderr={proc.stderr[-300:]})")
    return out


@app.get("/v1/models")
def models():
    return {"object": "list",
            "data": [{"id": m["id"], "object": "model", "owned_by": "opencode"} for m in BRIDGE_MODELS]}


@app.post("/v1/chat/completions")
async def chat(body: ChatIn):
    t0 = time.time()
    # Off the event loop: opencode runs 30-120s and must never stall polls/health.
    text = await asyncio.to_thread(_run_opencode_sync, _resolve(body.model), _prompt(body.messages, body.tools))
    call = _extract_call(text)
    if call:
        name, args = call
        return {"id": "chatcmpl-" + uuid.uuid4().hex[:12], "object": "chat.completion",
                "created": int(t0), "model": body.model,
                "choices": [{"index": 0,
                             "message": {"role": "assistant", "content": "",
                                         "tool_calls": [{"id": "call_" + uuid.uuid4().hex[:8], "type": "function",
                                                         "function": {"name": name, "arguments": json.dumps(args)}}]},
                             "finish_reason": "tool_calls"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
    return {"id": "chatcmpl-" + uuid.uuid4().hex[:12], "object": "chat.completion",
            "created": int(t0), "model": body.model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
