#!/usr/bin/env bash
# tpm-tools installer — copies the TPM agent and tpm-artifacts skill into the
# discovery paths of the chosen runtime. No config file edits required.
#
# Usage (default runtime: opencode):
#   curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/tpm-tools/main/install.sh | bash
#
# Pick a runtime:
#   curl -fsSL .../install.sh | TPM_TOOLS_RUNTIME=opencode bash
#   ./install.sh --runtime opencode
#   ./install.sh --list-runtimes
#
# Pin a branch/version:
#   TPM_TOOLS_BRANCH=v1.0.2 ./install.sh --runtime opencode
#
# Override the config dir (opencode only):
#   OPENCODE_CONFIG_DIR=/custom/path ./install.sh --runtime opencode

set -euo pipefail

# --- Config -----------------------------------------------------------------

REPO="DIAL-Studio/tpm-tools"
BRANCH="${TPM_TOOLS_BRANCH:-main}"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
RUNTIME="${TPM_TOOLS_RUNTIME:-opencode}"

# --- Helpers ----------------------------------------------------------------

cyan()   { printf "\033[36m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
die()    { red "error: $*" >&2; exit 1; }
has()    { command -v "$1" >/dev/null 2>&1; }

# --- Runtime registry -------------------------------------------------------
# Format per row: <id> <status> <default_config_root> <display>
# Status is one of: supported | planned
RUNTIME_TABLE=(
  "opencode   supported   \$HOME/.config/opencode   opencode (default)"
  "claude     planned     \$HOME/.claude             Claude Code"
  "copilot    planned     \$HOME/.github/copilot     GitHub Copilot Chat"
  "cursor     planned     \$HOME/.cursor             Cursor"
)

list_runtimes() {
  cyan "Available runtimes:"
  printf "  %-10s %-10s %-26s %s\n" "RUNTIME" "STATUS" "DEFAULT CONFIG ROOT" "TOOL"
  printf "  %-10s %-10s %-26s %s\n" "-------" "------" "--------------------" "----"
  for row in "${RUNTIME_TABLE[@]}"; do
    read -r id status root display <<< "$row"
    printf "  %-10s %-10s %-26s %s\n" "$id" "$status" "$root" "$display"
  done
  cat <<EOF

Only "supported" runtimes will install. "planned" runtimes print this list
and exit non-zero. Vote or track progress at:
  https://github.com/DIAL-Studio/tpm-tools/issues
EOF
}

usage() {
  cat <<EOF
tpm-tools installer

Usage:
  curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/tpm-tools/main/install.sh | bash
  curl -fsSL .../install.sh | TPM_TOOLS_RUNTIME=opencode bash
  ./install.sh --runtime opencode
  ./install.sh --list-runtimes
  ./install.sh --help

Flags:
  --runtime <id>       Choose runtime (default: opencode; see --list-runtimes)
  --list-runtimes      Print all known runtimes and exit
  -h, --help           Show this help

Environment:
  TPM_TOOLS_RUNTIME    Same as --runtime (useful for curl|bash)
  TPM_TOOLS_BRANCH     Pin a git ref (default: main ; e.g. v1.0.2)
  OPENCODE_CONFIG_DIR  Override opencode config root (default: ~/.config/opencode)
EOF
}

# --- Arg parsing ------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)        RUNTIME="${2:-}"; shift 2 ;;
    --runtime=*)      RUNTIME="${1#*=}"; shift ;;
    --list-runtimes)  list_runtimes; exit 0 ;;
    -h|--help)        usage; exit 0 ;;
    --)               shift; break ;;
    *)                die "Unknown flag: '$1'. Try --help." ;;
  esac
done

# --- Preflight --------------------------------------------------------------

if [[ -z "${HOME:-}" ]]; then
  die "HOME is not set. Cannot locate config directory."
fi

case "$(uname -s)" in
  Darwin|Linux|MINGW*|MSYS*|CYGWIN*) : ;;
  *) die "Unsupported OS: $(uname -s). See manual install in the README." ;;
esac

if ! has curl; then
  die "curl is required. Install it and re-run."
fi

# --- Resolve runtime --------------------------------------------------------

SKILL_URL="$BASE_URL/skills/tpm-artifacts/SKILL.md"

case "$RUNTIME" in
  opencode)
    OC_ROOT="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"
    SKILL_DIR="$OC_ROOT/skills/tpm-artifacts"
    AGENT_DIR="$OC_ROOT/agents"
    AGENT_FILE="$AGENT_DIR/tpm.md"
    AGENT_URL="$BASE_URL/agents/tpm.md"
    BINARY_NAME="opencode"
    BINARY_URL="https://opencode.ai"
    VERIFY_HINT="Press Tab to switch to the tpm primary agent."
    ;;
  claude|copilot|cursor)
    red "runtime '$RUNTIME' is planned but not yet supported."
    echo
    list_runtimes
    exit 2
    ;;
  "")
    die "No runtime specified. Use --runtime <id> or TPM_TOOLS_RUNTIME=<id>. See --list-runtimes."
    ;;
  *)
    die "Unknown runtime: '$RUNTIME'. See --list-runtimes."
    ;;
esac

cyan "Installing tpm-tools for runtime '$RUNTIME' into $OC_ROOT/"

# --- Soft presence check on the runtime binary ------------------------------

if ! has "$BINARY_NAME"; then
  yellow "warning: '$BINARY_NAME' not found on PATH."
  yellow "         Files will still be installed; install $BINARY_NAME from $BINARY_URL to use them."
fi

# --- Fetch ------------------------------------------------------------------

mkdir -p "$SKILL_DIR" "$AGENT_DIR"

tmp_skill="$(mktemp)"
tmp_agent="$(mktemp)"
trap 'rm -f "$tmp_skill" "$tmp_agent"' EXIT

cyan "Downloading SKILL.md..."
curl -fsSL "$SKILL_URL" -o "$tmp_skill" \
  || die "Failed to fetch SKILL.md from $BASE_URL"

cyan "Downloading agent file (tpm.md)..."
curl -fsSL "$AGENT_URL" -o "$tmp_agent" \
  || die "Failed to fetch tpm.md from $BASE_URL"

# Guard: validate frontmatter so a 404 page does not silently become a "skill"
if [[ ! -s "$tmp_skill" ]] || ! grep -q '^---' "$tmp_skill"; then
  die "SKILL.md download is empty or missing frontmatter. Check the URL or branch."
fi
if [[ ! -s "$tmp_agent" ]] || ! grep -q '^---' "$tmp_agent"; then
  die "Agent file download is empty or missing frontmatter. Check the URL or branch."
fi

# --- Install ----------------------------------------------------------------

backup_if_exists() {
  local f="$1"
  if [[ -f "$f" ]]; then
    local bak="${f}.bak.$(date +%s)"
    cp "$f" "$bak"
    yellow "Existing file backed up: $f -> $bak"
  fi
}

backup_if_exists "$SKILL_DIR/SKILL.md"
backup_if_exists "$AGENT_FILE"

mv "$tmp_skill" "$SKILL_DIR/SKILL.md"
mv "$tmp_agent"  "$AGENT_FILE"

green "Installed:"
green "  $SKILL_DIR/SKILL.md"
green "  $AGENT_FILE"

# --- Post-install hints ------------------------------------------------------

cat <<EOF

Next:
  1. If $BINARY_NAME was running, quit and restart it so it re-scans.
  2. $VERIFY_HINT
  3. Ask the tpm agent for a PRD / RICE / RFC — the skill loads on demand.

To uninstall:
  curl -fsSL $BASE_URL/uninstall.sh | TPM_TOOLS_RUNTIME=$RUNTIME bash

Branch: $BRANCH
Runtime: $RUNTIME
EOF