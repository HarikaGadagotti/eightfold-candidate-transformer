import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.pipeline import run_pipeline


def banner():
    print("=" * 60)
    print(" Eightfold Candidate Data Transformer")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Canonical Candidate Transformer")
    parser.add_argument("--csv", help="Recruiter CSV export")
    parser.add_argument("--ats-json", help="ATS JSON blob")
    parser.add_argument("--github", help="GitHub profile URL")
    parser.add_argument("--config", default="config/default_config.json", help="Projection configuration")
    parser.add_argument("--out", default="output.json", help="Output JSON file")
    args = parser.parse_args()

    banner()
    start = time.perf_counter()

    print("\nLoading input sources...")
    if args.csv:
        print(f"  ✓ Recruiter CSV : {args.csv}")
    if args.ats_json:
        print(f"  ✓ ATS JSON      : {args.ats_json}")
    if args.github:
        print(f"  ✓ GitHub        : {args.github}")

    print("\nRunning pipeline...")
    profiles = run_pipeline(args)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

    elapsed = round(time.perf_counter() - start, 3)

    print("\nPipeline completed successfully.\n")
    print("-" * 60)
    print(f"Profiles Generated : {len(profiles)}")
    print(f"Output File        : {args.out}")
    print(f"Execution Time     : {elapsed} sec")

    if profiles:
        avg = round(sum(p.get("overall_confidence", 0) for p in profiles) / len(profiles), 2)
        print(f"Average Confidence : {avg}")

    print("-" * 60)
    print("\nDone.\n")


if __name__ == "__main__":
    main()