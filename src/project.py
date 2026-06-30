import json

def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_path(obj, path):
    parts = path.replace("[]", "").split(".")
    cur = obj
    for p in parts:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return None
    return cur

def project(profile, config):
    out = {}
    for field_cfg in config["fields"]:
        target = field_cfg["path"]
        source_path = field_cfg.get("from", target)
        value = get_path(profile, source_path)

        # if config wants a single string but source is a list, take first element
        if isinstance(value, list) and field_cfg.get("type") == "string":
            value = value[0] if value else None

        if value is None:
            policy = config.get("on_missing", "null")
            if policy == "omit":
                continue
            elif policy == "error" and field_cfg.get("required"):
                raise ValueError(f"Required field missing: {target}")
            else:
                value = None

        out[target] = value

    if config.get("include_confidence"):
        out["provenance"] = profile.get("provenance", [])
        out["overall_confidence"] = profile.get("overall_confidence", 0)

    return out