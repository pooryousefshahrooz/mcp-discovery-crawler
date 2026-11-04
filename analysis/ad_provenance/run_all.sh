#!/bin/sh
# Ad-provenance pipeline. Re-runs every deterministic stage from the recorded responses;
# the two hand codings (out/coding_A.json, out/coding_B.json), coding/adjudication.json and
# coding/verification.json are inputs, not regenerated. Nothing is re-probed.
set -e
cd "$(dirname "$0")/../.."
python3 analysis/ad_provenance/s1_load_responses.py      # -> out/responses.jsonl
python3 analysis/ad_provenance/s2_detect_candidates.py   # -> out/candidates.jsonl, out/signatures.csv
python3 analysis/ad_provenance/coding/coder_A.py         # -> out/coding_A.json
python3 analysis/ad_provenance/s6_adjudicate.py          # -> out/agreement.json, out/disagreements.csv, out/final_codes.json
python3 analysis/ad_provenance/s7_quantify.py            # -> out/ad_items.csv, out/ad_provenance_results.csv,
                                                         #    out/ad_provenance_summary.json, out/fig_ad_provenance.{pdf,png}
# review sheets (only needed to re-code): s3_build_review_sheet.py [--exclude out/signatures_v1sheet.csv --out ...]
python3 analysis/ad_provenance/s8_sensitivity.py           # -> out/sensitivity.json
python3 analysis/ad_provenance/s9_audit_sample.py --score   # audit precision (verdicts in coding/audit_verdicts.csv)
