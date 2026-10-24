#!/usr/bin/env bash
set -euo pipefail
source ./bars_m3_common.sh
bars_m3_parse "$@"
bars_m3_require_variant
bars_m3_require_sha
[[ -z "$m3_analysis" ]] || { echo "Error: inference does not accept --analysis." >&2; exit 2; }
bash ./bars_inference.sh experiment=bars_ablation_inference "ablation_variant=$m3_variant" --checkpoint-sha256 "$m3_sha" "${m3_args[@]}"
