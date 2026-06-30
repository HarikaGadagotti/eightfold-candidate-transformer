import json

def extract(path):
    records = []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    for item in data:
        if not isinstance(item, dict):
            continue
        records.append({
            "source": "ats_json",
            "fields": {
                "full_name": item.get("candidate_name"),
                "email": item.get("contact_email"),
                "phone": item.get("contact_phone"),
                "current_company": item.get("employer"),
                "title": item.get("current_role") or None,
                "skills_raw": item.get("skills_list") or [],
            }
        })
    return records