from src.normalize import normalize_email, normalize_phone, normalize_name, normalize_skill
from src.confidence import field_confidence

PRIORITY = {
    "email": ["ats_json", "recruiter_csv", "resume", "github"],
    "phone": ["ats_json", "recruiter_csv"],
    "title": ["ats_json", "recruiter_csv"],
    "full_name": ["ats_json", "recruiter_csv", "github"],
    "current_company": ["ats_json", "recruiter_csv"],
}

def _bucket_key(records):
    for r in records:
        e = normalize_email(r["fields"].get("email"))
        if e:
            return e
    for r in records:
        p = normalize_phone(r["fields"].get("phone"))
        if p:
            return p
    for r in records:
        n = normalize_name(r["fields"].get("full_name"))
        if n:
            return n.lower()
    return None

def merge_all(all_records):
    """all_records: list of (record_dict) from every extractor, already flattened."""
    buckets = {}
    for rec in all_records:
        key = _bucket_key([rec])
        if key is None:
            continue
        buckets.setdefault(key, []).append(rec)

    merged_profiles = []
    for key, recs in buckets.items():
        profile = {"emails": set(), "phones": set(), "skills": {}, "provenance": []}
        for field, priority_list in PRIORITY.items():
            candidates = [r for r in recs if r["fields"].get(field)]
            candidates.sort(key=lambda r: priority_list.index(r["source"]) if r["source"] in priority_list else 99)
            if candidates:
                chosen = candidates[0]
                value = chosen["fields"][field]
                conf = field_confidence(chosen["source"], num_corroborating=len(candidates) - 1)
                profile[field] = value
                profile["provenance"].append({
                    "field": field, "source": chosen["source"],
                    "method": "priority_rule", "confidence": conf
                })

        for r in recs:
            e = normalize_email(r["fields"].get("email"))
            if e:
                profile["emails"].add(e)
            p = normalize_phone(r["fields"].get("phone"))
            if p:
                profile["phones"].add(p)
            for s in r["fields"].get("skills_raw", []) or []:
                norm = normalize_skill(s)
                if norm:
                    profile["skills"].setdefault(norm, {"sources": set(), "confidence": 0})
                    profile["skills"][norm]["sources"].add(r["source"])

        for skill, data in profile["skills"].items():
            data["confidence"] = field_confidence(
                "github" if "github" in data["sources"] else "ats_json",
                num_corroborating=len(data["sources"]) - 1
            )
            data["sources"] = list(data["sources"])  # set -> list, JSON-safe

        # convert skills dict into list-of-objects matching canonical schema
        profile["skills"] = [
            {"name": name, "confidence": data["confidence"], "sources": data["sources"]}
            for name, data in profile["skills"].items()
        ]
        profile["emails"] = list(profile["emails"])
        profile["phones"] = list(profile["phones"])
        merged_profiles.append(profile)

    return merged_profiles