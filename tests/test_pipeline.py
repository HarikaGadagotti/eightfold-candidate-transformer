import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argparse import Namespace
from src.pipeline import run_pipeline

def make_args(**kwargs):
    defaults = {"csv": None, "ats_json": None, "github": None,
                "config": "config/default_config.json"}
    defaults.update(kwargs)
    return Namespace(**defaults)

def test_csv_only():
    args = make_args(csv="samples/recruiter_export.csv")
    result = run_pipeline(args)
    assert len(result) == 3  # Jane Doe, Ravi Kumar, John Smith

def test_merge_csv_and_ats():
    args = make_args(csv="samples/recruiter_export.csv", ats_json="samples/ats_blob.json")
    result = run_pipeline(args)
    # All 3 candidates exist in both sources and share email -> still 3 profiles, not 6
    assert len(result) == 3
    names = [r["full_name"] for r in result]
    # ATS wins full_name priority -> "Jane A. Doe", not CSV's "Jane Doe"
    assert "Jane A. Doe" in names
    assert "John Smith" in names

def test_case_insensitive_email_merge():
    # CSV has "jane.doe@gmail.com", ATS has "Jane.Doe@gmail.com" -> must merge into ONE profile
    args = make_args(csv="samples/recruiter_export.csv", ats_json="samples/ats_blob.json")
    result = run_pipeline(args)
    jane = next(r for r in result if r["full_name"] == "Jane A. Doe")
    assert jane["emails"] == ["jane.doe@gmail.com"]  # single normalized email, not duplicated

def test_missing_phone_filled_from_other_source():
    # John has no phone in CSV but has one in ATS -> merged profile should have it
    args = make_args(csv="samples/recruiter_export.csv", ats_json="samples/ats_blob.json")
    result = run_pipeline(args)
    john = next(r for r in result if r["full_name"] == "John Smith")
    assert len(john["phones"]) == 1
    assert john["phones"][0].startswith("+1")

def test_missing_source_no_crash():
    args = make_args(csv="samples/does_not_exist.csv")
    result = run_pipeline(args)
    assert result == []

def test_malformed_ats_skipped(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    args = make_args(ats_json=str(bad_file))
    result = run_pipeline(args)
    assert result == []