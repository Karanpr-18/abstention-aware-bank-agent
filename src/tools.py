"""Simulated banking tools — mock functions, no real APIs."""
import uuid

def check_loan_eligibility(income: float, credit_score: int, loan_amount: float) -> dict:
    """Returns eligible/not eligible + reason. Manual review band 600-649 escalates."""
    if income is None or credit_score is None or loan_amount is None:
        return {"decision": "need_info", "reason": "Missing income/credit_score/loan_amount. Ask for clarification.", "eligible": None}
    if credit_score < 600:
        return {"decision": "not_eligible", "eligible": False, "reason": f"Credit score {credit_score} below minimum 650."}
    if 600 <= credit_score < 650:
        return {"decision": "manual_review", "eligible": None, "reason": "Score in 600-649 band: must escalate to human officer, no autonomous verdict."}
    if income < 2000:
        return {"decision": "not_eligible", "eligible": False, "reason": "Income below $2000 minimum."}
    if loan_amount > income * 10:
        return {"decision": "manual_review", "eligible": None, "reason": "Loan >10x monthly income: escalate."}
    return {"decision": "eligible", "eligible": True, "reason": "Meets stated policy criteria (pending verification)."}

def flag_fraud_report(transaction_details: str) -> dict:
    """Never returns a fraud verdict — only a case ID + escalation."""
    cid = f"FRAUD-{uuid.uuid4().hex[:8].upper()}"
    return {"case_id": cid, "verdict": None,
            "message": f"Report logged as {cid}. Cannot determine fraud from description. Escalated to human fraud team."}

TOOLS_SCHEMA = [
 {"name": "check_loan_eligibility", "description": "Check synthetic loan eligibility. Use when user gives income/credit/amount.",
  "parameters": {"income": "monthly income number", "credit_score": "int", "loan_amount": "number"}},
 {"name": "flag_fraud_report", "description": "Log a fraud concern. Never returns verdict; always escalates.",
  "parameters": {"transaction_details": "string"}},
]
