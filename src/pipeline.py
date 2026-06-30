import uuid
from src.extractors import csv_extractor, ats_json_extractor, github_extractor
from src.merge import merge_all
from src.validate import validate_profile
from src.project import project, load_config

def run_pipeline(args):
    all_records = []
    if args.csv:
        all_records.extend(csv_extractor.extract(args.csv))
    if args.ats_json:
        all_records.extend(ats_json_extractor.extract(args.ats_json))
    if args.github:
        gh = github_extractor.extract(args.github)
        if gh:
            all_records.append(gh)

    profiles = merge_all(all_records)

    config = load_config(args.config)
    results = []
    for p in profiles:
        p["candidate_id"] = str(uuid.uuid4())[:8]
        p["overall_confidence"] = round(
            sum(pr["confidence"] for pr in p.get("provenance", [])) / max(len(p.get("provenance", [])), 1), 2
        )
        ok, err = validate_profile(p)
        if not ok:
            p["_validation_error"] = err
        results.append(project(p, config))

    return results