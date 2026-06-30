import re
import phonenumbers
from dateutil import parser as dateparser

SKILL_SYNONYMS = {
    "js": "javascript",
    "javascript": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "py": "python",
    "python": "python",
    "node": "nodejs",
    "node.js": "nodejs",
    "aws": "aws",
    "amazon web services": "aws",
}

def normalize_phone(raw, default_region="IN"):
    if not raw:
        return None
    try:
        parsed = phonenumbers.parse(str(raw), default_region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None

def normalize_email(raw):
    if not raw or "@" not in str(raw):
        return None
    return str(raw).strip().lower()

def normalize_date(raw):
    if not raw:
        return None
    try:
        dt = dateparser.parse(str(raw))
        return dt.strftime("%Y-%m")
    except Exception:
        return None

def normalize_skill(raw):
    if not raw:
        return None
    key = re.sub(r"[^a-z0-9. ]", "", str(raw).lower().strip())
    return SKILL_SYNONYMS.get(key, key)

def normalize_name(raw):
    if not raw:
        return None
    return " ".join(str(raw).strip().split())