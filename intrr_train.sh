#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/intrr_common.sh"
intrr_main train "$@"
