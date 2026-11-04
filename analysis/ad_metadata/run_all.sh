#!/bin/sh
# Ad-metadata exposure study. Live probing (already done 2026-11-04, read-only, stops on 429):
#   python3 ad_probe/meta_tools_list.py && python3 ad_probe/meta_build_plan.py && python3 -u ad_probe/meta_probe.py 10
# Everything below re-runs offline from ad_probe/results/meta_2026-11/calls/*.jsonl.
set -e
cd "$(dirname "$0")/../.."
python3 analysis/ad_metadata/m1_detect.py --allow-uncoded     # lists signatures not seen in the v2 study
python3 analysis/ad_metadata/coding/code_new_signatures.py    # hand codes -> coding/new_signature_codes.json
python3 analysis/ad_metadata/m1_detect.py                     # -> out/responses.jsonl (ad-containing flag)
python3 analysis/ad_metadata/m2_extract.py                    # -> out/findings.jsonl, out/field_groups.csv
python3 analysis/ad_metadata/m3_metrics.py                    # review applied -> out/*.csv, out/metrics_summary.json
python3 analysis/ad_metadata/m4_figures.py                    # -> figs/fig_ad_metadata_{heatmap,heatmap_full,prevalence}.{pdf,png}
