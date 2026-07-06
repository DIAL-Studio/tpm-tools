#!/usr/bin/env bash
# tpm-tools uninstaller — removes the agent and skill installed by install.sh
# for the chosen runtime (default: opencode).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/tpm-tools/main/uninstall.sh | bash
#   ./uninstall.sh --runtime opencode
#   ./uninstall.sh --list-runtimes

set -euo pipefail

REPO="DIAL-Studio/tpm-tools"
BRANCH="${TPM_TOOLS_BRANCH:-main}"
RUNTIME="${TPM_TOOLS_RUNTIME:-opencode}"

green()  { printf "\033[32m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*"; }
cyan()   { printf "\033[36m%s\033[0m\n" "$*"; }
die()    { red "error: $*" >&2; exit 1; }

RUNTIME_TABLE=(
  "opencode   supported"
  "claude     planned"
  "copilot    planned"
  "cursor     planned"
)

list_runtimes() {
  cyan "Available runtimes:"
  printf "  %-10s %-10s\n" "RUNTIME" "STATUS"
  printf "  %-10s %-10s\n" "-------" "------"
  for row in "${RUNTIME_TABLE[@]}"; do
    read -r id status <<< "$row"
    printf "  %-10s %-10s\n" "$id" "$status"
  done
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)        RUNTIME="${2:-}"; shift 2 ;;
    --runtime=*)      RUNTIME="${1#*=}"; shift ;;
    --list-runtimes)  list_runtimes; exit 0 ;;
    -h|--help)
      cat <<EOF
tpm-tools uninstaller

Usage:
  ./uninstall.sh --runtime <id>
  curl -fsSL .../uninstall.sh | TPM_TOOLS_RUNTIME=opencode bash
EOF
      exit 0 ;;
    *) die "Unknown flag: '$1'." ;;
  esac
done

[[ -n "${HOME:-}" ]] || die "HOME is not set."

case "$RUNTIME" in
  opencode)
    OC_ROOT="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"
    TARGETS=("$OC_ROOT/skills/tpm-artifacts" "$OC_ROOT/agents/tpm.md")
    ;;
  claude|copilot|cursor)
    red "runtime '$RUNTIME' is planned but not yet supported."
    list_runtimes
    exit 2
    ;;
  "")
    die "No runtime specified. Use --runtime <id>." ;;
  *)
    die "Unknown runtime: '$RUNTIME'." ;;
esac

for t in "${TARGETS[@]}"; do
  if [[ -e "$t" ]]; then
    rm -rf "$t"
    green "Removed: $t"
  else
    yellow_msg="  (not present) $t"
    printf "\033[33m%s\033[0m\n" "$yellow_msg"
  fi
done

green "Restart '$RUNTIME' to reflect the change."
green "Done."