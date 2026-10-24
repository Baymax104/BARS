#!/usr/bin/env bash
set -euo pipefail
export UV_NO_SYNC="${UV_NO_SYNC:-1}"
source ./liger_common.sh
[[ "${NPROC_PER_NODE:-1}" == 1 ]] || { echo "Error: BARS formal inference requires one GPU process." >&2; exit 2; }

common_args=()
split="testing"
checkpoint_sha=""
deployment=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --deployment)
      [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || { echo "Error: BARS defaults to hybrid; --deployment requires hybrid." >&2; exit 2; }
      deployment="$2"; shift 2 ;;
    --deployment=*)
      deployment="${1#*=}"
      [[ -n "$deployment" ]] || { echo "Error: BARS defaults to hybrid; --deployment requires hybrid." >&2; exit 2; }
      shift ;;
    --checkpoint-sha256)
      [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || { echo "Error: --checkpoint-sha256 requires a value." >&2; exit 2; }
      checkpoint_sha="$2"; shift 2 ;;
    --checkpoint-sha256=*) checkpoint_sha="${1#*=}"; shift ;;
    --split)
      [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || { echo "Error: --split requires validation or testing." >&2; exit 2; }
      split="$2"
      shift 2
      ;;
    --split=*)
      split="${1#*=}"
      shift
      ;;
    ckpt_path=*|+ckpt_path=*|++ckpt_path=*)
      echo "Error: provide the selected formal checkpoint using --checkpoint." >&2
      exit 2
      ;;
    model.root.prediction_mode=*|+model.root.prediction_mode=*|++model.root.prediction_mode=*|inference_deployment_mode=*|+inference_deployment_mode=*|++inference_deployment_mode=*)
      case "${1#*=}" in
        hybrid|'"hybrid"'|"'hybrid'") ;;
        *) echo "Error: BARS evaluation uses hybrid; dense evaluation is retired." >&2; exit 2 ;;
      esac
      common_args+=("$1"); shift ;;
    --data-dir|--semantic-id-path|--embedding-path|--checkpoint|--dataset|--devices|--notes|--group|--seed|--master-port)
      [[ $# -ge 2 ]] || { echo "Error: $1 requires a non-empty value." >&2; exit 2; }
      common_args+=("$1" "$2")
      shift 2
      ;;
    *)
      [[ -n "${1//[[:space:]]/}" ]] || { echo "Error: empty Hydra override." >&2; exit 2; }
      common_args+=("$1")
      shift
      ;;
  esac
done

[[ "$checkpoint_sha" =~ ^[0-9a-f]{64}$ ]] || { echo "Error: --checkpoint-sha256 requires 64 lowercase hex characters." >&2; exit 2; }
case "$split" in
  validation) split_args=(evaluation_split=validation evaluation_data_folder=evaluation) ;;
  testing) split_args=(evaluation_split=testing evaluation_data_folder=testing) ;;
  *) echo "Error: --split requires validation or testing." >&2; exit 2 ;;
esac
deployment_args=("model.root.prediction_mode=hybrid")
if [[ -n "$deployment" ]]; then
  case "$deployment" in
    hybrid) ;;
    *) echo "Error: BARS evaluation uses hybrid; dense evaluation is retired." >&2; exit 2 ;;
  esac
fi

liger_launch inference experiment=bars_inference "checkpoint_sha256=\"$checkpoint_sha\"" "${split_args[@]}" "${deployment_args[@]}" "${common_args[@]}"
