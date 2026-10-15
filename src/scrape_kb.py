"""
Scrape entire FAQ/policy pages from top global banks.
Saves raw markdown + metadata to kb_raw/
Sources: US / China / India / France / Germany / Switzerland / Spain / Japan
Run: .venv/bin/python src/scrape_kb.py
"""
import os, re, json, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

KB_RAW = Path(os.environ.get("KB_RAW_DIR", "./kb_raw"))
KB_RAW.mkdir(parents=True, exist_ok=True)

# Curated stable FAQ / help / fraud pages. Entire page text is extracted.
SOURCES = [
    # US — all verified 200
    {"country": "USA", "bank": "Chase", "topic": "mortgage_qualify", "url": "https://www.chase.com/personal/mortgage/education/financing-a-home/how-to-qualify-for-a-mortgage"},
    {"country": "USA", "bank": "Chase", "topic": "mortgage_docs", "url": "https://www.chase.com/personal/mortgage/education/financing-a-home/mortgage-application"},
    {"country": "USA", "bank": "Chase", "topic": "auto_faq", "url": "https://autofinance.chase.com/auto-finance/faqs"},
    {"country": "USA", "bank": "Bank_of_America", "topic": "mortgage_faq", "url": "https://www.bankofamerica.com/mortgage/faqs"},
    {"country": "USA", "bank": "Bank_of_America", "topic": "security", "url": "https://www.bankofamerica.com/security-center/overview/"},
    {"country": "USA", "bank": "Citi", "topic": "fraud_protection", "url": "https://www.citi.com/tts/solutions/commercial-cards/fraud-protection"},
    {"country": "USA", "bank": "Citi", "topic": "cards_knowledge", "url": "https://www.citi.com/credit-cards/knowledge-center"},
    # China
    {"country": "China", "bank": "ICBC", "topic": "personal_loan", "url": "https://www.icbc.com.cn/ICBC/EN/PersonalFinance/PersonalLoan/PersonalBusinessLoan"},
    {"country": "China", "bank": "ICBC", "topic": "security_column", "url": "https://www.icbc.com.cn/en/column/1438058474352558360.html"},
    {"country": "China", "bank": "Bank_of_China", "topic": "service", "url": "https://www.bankofchina.com/en/customer-service/"},
    {"country": "China", "bank": "Bank_of_China", "topic": "cards", "url": "https://www.bankofchina.com/en/cc/"},
    # India
    {"country": "India", "bank": "SBI", "topic": "personal_loan", "url": "https://sbi.co.in/web/personal-banking/loans/personal-loans"},
    {"country": "India", "bank": "SBI", "topic": "faq_personal_loan", "url": "https://www.sbi.co.in/web/faq-s/faq-personal-loan"},
    {"country": "India", "bank": "HDFC", "topic": "personal_loan_eligibility", "url": "https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan/eligibility"},
    {"country": "India", "bank": "HDFC", "topic": "home_loan_faq", "url": "https://homeloans.hdfc.bank.in/checklist/faqs"},
    # France
    {"country": "France", "bank": "BNP_Paribas", "topic": "invest_faq", "url": "https://invest.bnpparibas/en/faq"},
    {"country": "France", "bank": "BNP_Paribas", "topic": "fraud_prevention", "url": "https://cashmanagement.bnpparibas.com/solutions/prevention-against-fraud-cyber-risks"},
    {"country": "France", "bank": "Societe_Generale", "topic": "contact", "url": "https://www.societegenerale.com/en/contact-us"},
    {"country": "France", "bank": "Societe_Generale", "topic": "infosec", "url": "https://www.societegenerale.com/en/information-security"},
    # Germany
    {"country": "Germany", "bank": "Deutsche_Bank", "topic": "personal_loan_faq", "url": "https://www.deutsche.bank.in/en/loans/personal-loan-faqs.html"},
    {"country": "Germany", "bank": "Deutsche_Bank", "topic": "security", "url": "https://security.db.com"},
    {"country": "Germany", "bank": "Commerzbank", "topic": "contact", "url": "https://www.commerzbank.de/group/service/contact"},
    {"country": "Germany", "bank": "Commerzbank", "topic": "security_warnings", "url": "https://www.commerzbank.com/corporateclients/security-warnings"},
    # Switzerland — ubs.com blocks python-requests (403) but serves real content to webfetch; keep both, scraper falls back
    {"country": "Switzerland", "bank": "UBS", "topic": "phishing_global", "url": "https://www.ubs.com/global/en/our-firm/cybersafe/phishing.html"},
    {"country": "Switzerland", "bank": "UBS", "topic": "security_digital", "url": "https://www.ubs.com/ch/en/services/digital-banking/security.html"},
    # Spain
    {"country": "Spain", "bank": "Santander", "topic": "fraud_fight", "url": "https://www.santander.com/en/press-room/press-releases/2023/07/banco-santander-bbva-and-caixabank-join-forces-to-fight-fraud"},
    {"country": "Spain", "bank": "Santander", "topic": "support_hub", "url": "https://www.santander.co.uk/personal/support"},
    {"country": "Spain", "bank": "BBVA", "topic": "fraud_fight", "url": "https://www.bbva.com/en/innovation/bbva-banco-santander-and-caixabank-join-forces-to-fight-financial-fraud"},
    {"country": "Spain", "bank": "BBVA", "topic": "contact", "url": "https://www.bbva.com/en/contact"},
    # Japan
    {"country": "Japan", "bank": "MUFG", "topic": "fraud_report", "url": "https://www.mufgamericas.com/report-suspicious-activity"},
    {"country": "Japan", "bank": "MUFG", "topic": "financial_crimes", "url": "https://www.bk.mufg.jp/global/aboutus/financialcrimes.html"},
    {"country": "Japan", "bank": "MUFG", "topic": "faqs", "url": "https://www.mufg.jp/english/faqs/index.html"},
    {"country": "Japan", "bank": "SMBC", "topic": "security_americas", "url": "https://www.smbcgroup.com/americas/Security"},
    {"country": "Japan", "bank": "SMBC", "topic": "security_prestia", "url": "https://www.smbctb.co.jp/en/service/security/"},
]
# Real bank POLICY docs (terms, account T&Cs, fraud/security policies). HTML only here;
# PDFs + bot-blocked pages are listed for MANUAL download (see MANUAL_NEEDED below).
POLICY_SOURCES = [
    {"country": "USA", "bank": "Chase", "topic": "policy_terms_of_use", "url": "https://www.chase.com/digital/resources/terms-of-use"},
    {"country": "USA", "bank": "Chase", "topic": "policy_privacy", "url": "https://www.chase.com/digital/resources/privacy-security/privacy/online-privacy-policy"},
    {"country": "USA", "bank": "Bank_of_America", "topic": "policy_privacy", "url": "https://www.bankofamerica.com/security-center/privacy-overview"},
    {"country": "USA", "bank": "Citi", "topic": "policy_privacy_notice", "url": "https://www.citi.com/policies/us-privacy-notice-for-consumers"},
    {"country": "China", "bank": "Bank_of_China", "topic": "policy_ebanking_terms_uk", "url": "https://www.bankofchina.com/uk/custserv/cs2/201109/t20110928_1578065.html"},
    {"country": "China", "bank": "Bank_of_China", "topic": "policy_account_terms_sg", "url": "https://www.bankofchina.com/sg/bocinfo/bi5/201407/t20140701_3567090.html"},
    {"country": "India", "bank": "SBI", "topic": "policy_terms_of_service", "url": "https://sbi.bank.in/web/customer-care/citizens-charter/general-terms-and-conditions-of-service"},
    {"country": "India", "bank": "SBI", "topic": "policy_account_terms_uk", "url": "https://sbiuk.statebank/general-terms-conditions"},
    {"country": "India", "bank": "HDFC", "topic": "policy_terms", "url": "https://www.hdfc.bank.in/terms-and-conditions"},
    {"country": "India", "bank": "HDFC", "topic": "policy_privacy", "url": "https://www.hdfc.bank.in/privacy-policy"},
    {"country": "France", "bank": "BNP_Paribas", "topic": "policy_legal", "url": "https://usa.bnpparibas/en/legal-information/"},
    {"country": "France", "bank": "BNP_Paribas", "topic": "policy_complaints", "url": "https://usa.bnpparibas/en/complaints-management-policy/"},
    {"country": "France", "bank": "Societe_Generale", "topic": "policy_legal", "url": "https://www.societegenerale.com/en/legal-information"},
    {"country": "Germany", "bank": "Deutsche_Bank", "topic": "policy_conditions_nl", "url": "https://country.db.com/netherlands/about-us/general-information-and-conditions"},
    {"country": "Germany", "bank": "Deutsche_Bank", "topic": "policy_security_hub", "url": "https://security.db.com/index?language_id=1"},
    {"country": "Germany", "bank": "Commerzbank", "topic": "policy_terms", "url": "https://www.commerzbank.com/corporateclients/terms"},
    {"country": "Spain", "bank": "Santander", "topic": "policy_fraud_uk", "url": "https://www.santander.co.uk/personal/support/fraud-and-security"},
    {"country": "Spain", "bank": "Santander", "topic": "policy_security_us", "url": "https://www.santanderbank.com/personal/security-center"},
    {"country": "Spain", "bank": "BBVA", "topic": "policy_legal_notice", "url": "https://shareholdersandinvestors.bbva.com/legal-notice"},
    {"country": "Spain", "bank": "BBVA", "topic": "policy_security", "url": "https://shareholdersandinvestors.bbva.com/security/"},
    {"country": "Japan", "bank": "MUFG", "topic": "policy_terms", "url": "https://www.bk.mufg.jp/global/termsandconditions/index.html"},
    {"country": "Japan", "bank": "MUFG", "topic": "policy_fraud_notice", "url": "https://www.bk.mufg.jp/global/noticeaboutfraud/index.html"},
    {"country": "Japan", "bank": "SMBC", "topic": "policy_terms_global", "url": "https://www.smbc.co.jp/global/terms"},
    {"country": "Japan", "bank": "SMFG", "topic": "policy_terms", "url": "https://www.smfg.co.jp/english/terms/"},
    {"country": "Switzerland", "bank": "UBS", "topic": "policy_disclaimer", "url": "https://www.ubs.com/global/en/legal/disclaimer.html"},
    {"country": "Switzerland", "bank": "UBS", "topic": "policy_cybersafe", "url": "https://www.ubs.com/global/en/our-firm/cybersafe.html"},
]
SOURCES = SOURCES + POLICY_SOURCES
# Anything the scripted scraper cannot fetch (PDF-only or 403 bot-block) — download manually to kb_raw/
MANUAL_NEEDED = [
    "BofA Deposit Agreement PDF: https://www.bankofamerica.com/salesservices/deposits/resources/deposit-agreements",
    "Citi Consumer Deposit Account Agreement PDF: https://online.citi.com/JRS/popups/ao/CDAA.pdf",
    "ICBC London Business Account T&Cs PDF: https://v.icbc.com.cn/userfiles/Resources/ICBC/haiwai/ICBCLondon/download/2024/BusinessAccountTermsConditions_SUB_v17_01122024.pdf",
    "ICBC Singapore Card T&Cs PDF: https://v.icbc.com.cn/userfiles/resources/icbc/haiwai/singapore/download/2025/overall_tc.pdf",
    "UBS phishing + security pages (ubs.com 403-blocks python-requests; already saved via webfetch but manual HTML download preferred for reproducibility)",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
           "Accept-Language": "en-US,en;q=0.9"}

def extract_full_page(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    if HAS_TRAFILATURA:
        dl = trafilatura.fetch_url(url)
        if dl:
            txt = trafilatura.extract(dl, include_comments=False, include_tables=True)
            if txt and len(txt.strip()) > 500:
                return txt.strip()
    # fallback: BeautifulSoup full-text
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def main():
    manifest = []
    for s in SOURCES:
        fname = f"{s['country']}_{s['bank']}_{s['topic']}.md".replace("/", "_")
        out = KB_RAW / fname
        try:
            print(f"FETCH {s['bank']} [{s['country']}] {s['url']}")
            txt = extract_full_page(s["url"])
            header = f"# {s['bank']} ({s['country']}) — {s['topic']}\nSource: {s['url']}\n\n"
            out.write_text(header + txt, encoding="utf-8")
            print(f"  -> {len(txt)} chars -> {fname}")
            manifest.append({**s, "file": fname, "chars": len(txt), "status": "ok"})
        except Exception as e:
            print(f"  FAILED: {e}")
            manifest.append({**s, "file": fname, "chars": 0, "status": f"fail: {e}"})
        time.sleep(1)
    (KB_RAW / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ok = sum(1 for m in manifest if m["status"] == "ok")
    print(f"\nDone {ok}/{len(manifest)} pages. See kb_raw/manifest.json")

if __name__ == "__main__":
    main()
