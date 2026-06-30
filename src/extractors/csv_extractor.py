import csv

def extract(path):
    records = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("email") and not row.get("name"):
                    continue  # skip garbage row
                records.append({
                    "source": "recruiter_csv",
                    "fields": {
                        "full_name": row.get("name"),
                        "email": row.get("email"),
                        "phone": row.get("phone"),
                        "current_company": row.get("current_company"),
                        "title": row.get("title"),
                    }
                })
    except FileNotFoundError:
        return []
    return records