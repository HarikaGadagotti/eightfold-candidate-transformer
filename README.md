# Eightfold Candidate Data Transformer

Transforms messy multi-source candidate data (recruiter CSV, ATS JSON, GitHub profiles)
into one clean, canonical, schema-validated candidate profile per person — with full
provenance and confidence scoring.

**Design Document:** [Harika_Gadagotti_harikagadagotti@gmail.com_Eightfold.pdf](./Harika_Gadagotti_harikagadagotti@gmail.com_Eightfold.pdf)

## Demo Video

[Watch here](https://www.loom.com/share/c7d024df961745809ee3ec54102434e4)

## Repository Contents

- `src/`, `cli.py` — Core pipeline implementation
- `config/` — Default and custom output configurations
- `samples/` — Sample recruiter CSV and ATS JSON inputs
- `output_default.json`, `output_custom.json`, `output_with_github.json` — Sample outputs generated from the provided inputs
- `tests/test_pipeline.py` — Automated test suite (6 test cases)
- `Harika_Gadagotti_harikagadagotti@gmail.com_Eightfold.pdf` — One-page technical design document


## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run — default schema

```bash
python cli.py --csv samples/recruiter_export.csv --ats-json samples/ats_blob.json --config config/default_config.json --out output_default.json
```

## Run — custom config (renamed/filtered fields)

```bash
python cli.py --csv samples/recruiter_export.csv --ats-json samples/ats_blob.json --config config/custom_config_example.json --out output_custom.json
```

## Run — with GitHub as the unstructured source

```bash
python cli.py --csv samples/recruiter_export.csv --ats-json samples/ats_blob.json --github https://github.com/torvalds --config config/default_config.json --out output_with_github.json
```

## Run tests

```bash
pytest tests/ -v
```
6 tests covering: CSV-only extraction, CSV+ATS merge, case-insensitive email matching across sources, filling a missing field from a corroborating source, a missing/nonexistent source file, and malformed JSON input.

## Architecture

`extract → normalize → merge → confidence → project → validate`

- **extract**: each source has its own extractor returning a uniform `{source, fields}` shape (`src/extractors/`)
- **normalize**: phone → E.164 via `phonenumbers` (rejects unassigned/placeholder numbers rather than storing them), date → `YYYY-MM` via `dateutil`, skills → lowercased canonical names via a synonym map, emails → lowercased and trimmed
- **merge**: candidates are bucketed by normalized email → phone → name (in that priority). For each field, a source-priority table decides the winning value on conflict (`src/merge.py`)
- **confidence**: `base_source_reliability × (1 + 0.15 × num_corroborating_sources)`, capped at 1.0 (`src/confidence.py`)
- **project**: a separate layer reads `config.json` and reshapes the canonical record into the requested output (rename, filter, type-coerce, toggle provenance) — the merge engine never knows about output shape (`src/project.py`)
- **validate**: final JSON is checked against the canonical schema plus targeted rules — email/phone format, duplicate emails/phones, confidence bounds, skill shape — before being written (`src/validate.py`)

## Source priority rules (and why)

| Field | Priority order | Reasoning |
|---|---|---|
| email/phone | ATS > Recruiter CSV > Resume | ATS data is typically HR-verified |
| full_name, title | ATS > Recruiter CSV > GitHub | Same reasoning |
| skills | GitHub (repository languages) > Resume (self-reported skills) | Repository languages provide evidence of technologies used, while resume skills are self-reported. |

## Edge cases handled

- Missing source file → extractor returns `[]`/`None`, pipeline continues, never crashes
- Malformed JSON → caught, treated as an empty source
- CSV row missing both name and email → skipped silently
- Same candidate across CSV + ATS with case-mismatched email (`Jane.Doe@` vs `jane.doe@`) → still merges into one profile via lowercased matching
- A field present in one source but missing in another (e.g. phone missing in CSV, present in ATS) → filled from the available source instead of left null
- Invalid/placeholder phone numbers (failing real-number validation, e.g. fake area codes) → dropped to `null` rather than stored as a confident-but-wrong value
- GitHub user with no public email → profile still created from other fields, lower confidence, empty `emails: []`

## Deliberately descoped (time-boxed decisions)

- Resume PDF/DOCX parsing — not implemented; extractor interface is identical to existing ones, so it's a drop-in addition, not a redesign
- LinkedIn profile extraction — no public API without scraping/auth, so excluded
- Fuzzy name-matching for merge fallback (e.g. via `rapidfuzz`) — current merge relies on exact normalized email/phone/name match, sufficient for the provided samples but would need fuzzy matching at production scale with noisier data

## Tech stack

Python 3.13, `phonenumbers`, `python-dateutil`, `requests`, `jsonschema`, `pytest`