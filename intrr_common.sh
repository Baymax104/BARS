#!/usr/bin/env bash
# IntRR 仅处理参数；训练和推理均进入统一 src.main。
intrr_quote() {
  local value="$1" quoted='"' backslashes=0 index char count
  # Hydra只在引号前解释反斜杠转义；普通路径中的反斜杠原样保留。
  for (( index=0; index<${#value}; index++ )); do
    char="${value:index:1}"
    if [[ "$char" == '\' ]]; then backslashes=$((backslashes + 1)); continue; fi
    if [[ "$char" == '"' ]]; then
      for (( count=0; count<2*backslashes+1; count++ )); do quoted+='\'; done
    else
      for (( count=0; count<backslashes; count++ )); do quoted+='\'; done
    fi
    quoted+="$char"; backslashes=0
  done
  for (( count=0; count<2*backslashes; count++ )); do quoted+='\'; done
  printf '%s"' "$quoted"
}

intrr_main() {
  [[ -f src/main.py ]] || { echo 'Error: run from the GRID repository root.' >&2; return 2; }
  local mode="$1"
  shift
  local processes devices port data_dir="" sid="" quantizer="" checkpoint=""
  local notes="" seed=42 wandb_group=intrr dry_run=false option value
  local -a extra=() args=()
  if [[ "$mode" == train ]]; then
    processes="${NPROC_PER_NODE:-2}"
    devices="${DEVICES:-[0,1]}"
  else
    processes="${NPROC_PER_NODE:-1}"
    devices="${DEVICES:-[0]}"
  fi
  port="${MASTER_PORT:-29500}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) dry_run=true; shift; continue ;;
      --data-dir|--semantic-id-path|--group|--wandb-group|--ckpt-path|--checkpoint|--notes|--seed|--devices|--master-port)
        option="$1"
        [[ $# -ge 2 && -n "${2//[[:space:]]/}" && "$2" != --* ]] || {
          echo "Error: $option requires a non-empty value." >&2; return 2;
        }
        value="$2"; shift 2 ;;
      --data-dir=*|--semantic-id-path=*|--group=*|--wandb-group=*|--ckpt-path=*|--checkpoint=*|--notes=*|--seed=*|--devices=*|--master-port=*)
        option="${1%%=*}"; value="${1#*=}"; shift
        [[ -n "${value//[[:space:]]/}" ]] || {
          echo "Error: $option requires a non-empty value." >&2; return 2;
        } ;;
      --*) echo "Error: unknown option $1." >&2; return 2 ;;
      *=*) extra+=("$1"); shift; continue ;;
      *) echo "Error: expected a launcher option or Hydra override: $1." >&2; return 2 ;;
    esac
    case "$option" in
      --data-dir) data_dir="$value" ;;
      --semantic-id-path) sid="$value" ;;
      --group) quantizer="$value" ;;
      --wandb-group) wandb_group="$value" ;;
      --ckpt-path|--checkpoint) checkpoint="$value" ;;
      --notes) notes="$value" ;;
      --seed) seed="$value" ;;
      --devices) devices="$value" ;;
      --master-port) port="$value" ;;
    esac
  done
  [[ -n "$data_dir" && -n "$sid" && -n "$notes" ]] || {
    echo 'Error: --data-dir, --semantic-id-path and --notes are required.' >&2; return 2;
  }
  case "$quantizer" in
    rkmeans|rvq|rqvae) ;;
    *) echo 'Error: --group requires rkmeans, rvq or rqvae.' >&2; return 2 ;;
  esac
  [[ "$seed" =~ ^[0-9]+$ ]] || { echo 'Error: invalid seed.' >&2; return 2; }
  [[ "$processes" =~ ^[1-9][0-9]*$ ]] || { echo 'Error: invalid process count.' >&2; return 2; }
  [[ "$port" =~ ^[0-9]{1,5}$ ]] && (( 10#$port >= 1 && 10#$port <= 65535 )) || {
    echo 'Error: invalid master port.' >&2; return 2;
  }
  [[ "$devices" =~ ^\[[0-9]+(,[[:space:]]*[0-9]+)*\]$ ]] || {
    echo 'Error: --devices requires an integer device list.' >&2; return 2;
  }
  if [[ "$mode" == inference && -z "$checkpoint" ]]; then
    echo 'Error: --ckpt-path is required for inference.' >&2; return 2
  fi
  args=(
    "experiment=intrr_$mode"
    "data_dir=$(intrr_quote "$data_dir")"
    "semantic_id_path=$(intrr_quote "$sid")"
    "sid_type=$quantizer" "group=$(intrr_quote "$wandb_group")"
    "seed=$seed" "devices=$devices"
    "logger.wandb.notes=$(intrr_quote "$notes")"
  )
  if [[ -n "$checkpoint" ]]; then args+=("ckpt_path=$(intrr_quote "$checkpoint")"); fi
  if [[ "$dry_run" == true ]]; then args+=(--dry-run); fi
  args+=("${extra[@]}")
  OMP_NUM_THREADS=$(( $(nproc) / processes )) \
    uv run torchrun --nproc_per_node="$processes" --master_port="$port" -m src.main "${args[@]}"
}
