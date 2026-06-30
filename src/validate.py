import re
import jsonschema

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+\d{8,15}$")

SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "full_name": {"type": ["string", "null"]},
        "headline": {"type": ["string", "null"]},
        "current_company": {"type": ["string", "null"]},
        "title": {"type": ["string", "null"]},
        "emails": {"type": "array", "items": {"type": "string"}},
        "phones": {"type": "array", "items": {"type": "string"}},
        "skills": {"type": "array"},
        "overall_confidence": {"type": "number"},
        "provenance": {"type": "array"},
        "metadata": {"type": "object"}
    },
    "required": ["candidate_id"]
}

def validate_profile(profile):
    try:
        jsonschema.validate(instance=profile, schema=SCHEMA)
    except jsonschema.ValidationError as e:
        return False, str(e)

    for email in profile.get("emails", []):
        if not EMAIL_REGEX.match(email):
            return False, f"Invalid email: {email}"

    for phone in profile.get("phones", []):
        if not PHONE_REGEX.match(phone):
            return False, f"Invalid phone: {phone}"

    emails = profile.get("emails", [])
    if len(emails) != len(set(emails)):
        return False, "Duplicate emails found"

    phones = profile.get("phones", [])
    if len(phones) != len(set(phones)):
        return False, "Duplicate phone numbers found"

    confidence = profile.get("overall_confidence", 0)
    if confidence < 0 or confidence > 1:
        return False, "overall_confidence must be between 0 and 1"

    for skill in profile.get("skills", []):
        if "name" not in skill:
            return False, "Skill missing name"
        if "confidence" not in skill:
            return False, "Skill missing confidence"
        if skill["confidence"] < 0 or skill["confidence"] > 1:
            return False, "Invalid skill confidence"

    return True, None