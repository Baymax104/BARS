#!/usr/bin/env bash
set -euo pipefail
source ./bars_m3_common.sh
bars_m3_parse "$@"
bars_m3_require_variant
[[ -z "$m3_analysis" && -z "$m3_sha" ]] || { echo "Error: training does not accept diagnosis/checkpoint identity." >&2; exit 2; }
bash ./bars_train.sh experiment=bars_ablation_train "ablation_variant=$m3_variant" "${m3_args[@]}"
