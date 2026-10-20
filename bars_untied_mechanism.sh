#!/usr/bin/env bash
set -euo pipefail
export UV_NO_SYNC="${UV_NO_SYNC:-1}"
source ./liger_common.sh
source ./copmrec_m3_common.sh
[[ "${NPROC_PER_NODE:-1}" == 1 ]] || { echo "Error: mechanism analysis requires one process." >&2; exit 2; }
copmrec_m3_parse "$@"
[[ -z "$m3_variant" ]] || { echo "Error: mechanism analysis has a fixed Untied source; omit --variant." >&2; exit 2; }
identity_args=()
case "$m3_analysis" in
  contributions)
    [[ -z "$m3_sha" && -z "$m3_checkpoint" ]] || { echo "Error: contributions reads predictions, not a checkpoint." >&2; exit 2; }
    experiment=bars_untied_contributions ;;
  generation)
    copmrec_m3_require_sha
    [[ -n "$m3_checkpoint" && "$m3_checkpoint" != null ]] || { echo "Error: generation requires --checkpoint." >&2; exit 2; }
    identity_args+=("checkpoint_sha256=\"$m3_sha\"")
    experiment=bars_untied_mechanism ;;
  *) echo "Error: --analysis requires contributions or generation." >&2; exit 2 ;;
esac
# 复用公共参数解析；experiment.run_mode=analysis统一调用Trainer.test。
liger_launch train "experiment=$experiment" "${identity_args[@]}" "${m3_args[@]}"
