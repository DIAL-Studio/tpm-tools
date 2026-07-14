#!/usr/bin/env bash
# pm-agent-harness-kit installer — interactive TUI + silent mode.
#
# Interactive (default — prompts for runtime and path):
#   curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/install.sh | bash
#
# Silent (non-interactive, with explicit runtime):
#   curl .../install.sh | TPM_TOOLS_RUNTIME=claude-code bash
#   ./install.sh --runtime opencode
#   ./install.sh --runtime claude-code --non-interactive
#   ./install.sh --list-runtimes

set -euo pipefail

# --- Config -----------------------------------------------------------------
REPO="DIAL-Studio/pm-agent-harness-kit"
BRANCH="${TPM_TOOLS_BRANCH:-main}"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
ARCHIVE_URL="https://github.com/${REPO}/archive/${BRANCH}.tar.gz"
RUNTIME="${TPM_TOOLS_RUNTIME:-}"
SCOPE="${TPM_TOOLS_SCOPE:-}"
WITH_MCP=false
NON_INTERACTIVE=false
SKILL_COUNT=0

# --- Colors and helpers -----------------------------------------------------
BOLD="\033[1m"
DIM="\033[2m"
RESET="\033[0m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
MAGENTA="\033[35m"

green()  { printf "${GREEN}%s${RESET}\n" "$*"; }
cyan()   { printf "${CYAN}%s${RESET}\n" "$*"; }
yellow() { printf "${YELLOW}%s${RESET}\n" "$*"; }
red()    { printf "${RED}%s${RESET}\n" "$*" >&2; }
bold()   { printf "${BOLD}%s${RESET}\n" "$*"; }
dim()    { printf "${DIM}%s${RESET}\n" "$*"; }
magenta(){ printf "${MAGENTA}%s${RESET}\n" "$*"; }
die()    { red "error: $*" >&2; exit 1; }
has()    { command -v "$1" >/dev/null 2>&1; }

# --- Helpers: box drawing ---------------------------------------------------

box_top()    { printf "  ${BOLD}╔%s╗${RESET}\n" "$(printf '═%.0s' $(seq 1 $((COLUMNS-6)) ))"; }
box_bot()    { printf "  ${BOLD}╚%s╝${RESET}\n" "$(printf '═%.0s' $(seq 1 $((COLUMNS-6)) ))"; }
box_line()   { printf "  ${BOLD}║${RESET} %-$((${COLUMNS}-8))s ${BOLD}║${RESET}\n" "$*"; }
box_title()  { printf "  ${BOLD}║${RESET}${MAGENTA} %s${RESET}\n" "$*"; }
separator()  { printf "  ${DIM}─────────────────────────────────────────────────────${RESET}\n"; }

COLUMNS="${COLUMNS:-80}"

runtimes() {
  cat <<TABLE
  ${BOLD}Available runtimes:${RESET}
    1) opencode     (default) — opencode
    2) claude-code             — Claude Code
    3) copilot                 — GitHub Copilot (planned — installs files, runtime TBD)
    4) codex                   — OpenAI Codex   (planned — installs files, runtime TBD)
TABLE
}

list_runtimes() {
  cyan "Available runtimes:"
  printf "  %-12s %s\n" "opencode"   "opencode (default) — supported"
  printf "  %-12s %s\n" "claude-code" "Claude Code — supported"
  printf "  %-12s %s\n" "copilot"    "GitHub Copilot (planned)"
  printf "  %-12s %s\n" "codex"      "OpenAI Codex (planned)"
  echo ""
  echo 'Only "supported" runtimes will install. "planned" runtimes exit non-zero.'
  echo "Track progress at: https://github.com/DIAL-Studio/pm-agent-harness-kit/issues"
}

usage() {
  cat <<EOF
pm-agent-harness-kit installer — 7 PM agents + 59 skills

Usage:
  curl -fsSL $BASE_URL/install.sh | bash
  curl .../install.sh | TPM_TOOLS_RUNTIME=claude-code bash
  ./install.sh --runtime opencode
  ./install.sh --list-runtimes

Flags:
  --runtime <id>       Choose runtime (silent mode — no prompts)
  --scope <id>         Install globally or in current project (global|project)
  --with-mcp           Also install MCP harness (initiative backlog, audit trail)
  --non-interactive    Fail if --runtime is not set
  --list-runtimes      Print all known runtimes and exit
  -h, --help           Show this help

Environment:
  TPM_TOOLS_RUNTIME      Same as --runtime
  TPM_TOOLS_SCOPE        Same as --scope (global|project)
  TPM_TOOLS_BRANCH       Pin a git ref (default: main)
  OPENCODE_CONFIG_DIR    Override opencode config root (default: ~/.config/opencode)
EOF
}

# --- Arg parsing ------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)           RUNTIME="${2:-}"; shift 2 ;;
    --runtime=*)         RUNTIME="${1#*=}"; shift ;;
    --scope)             SCOPE="${2:-}"; shift 2 ;;
    --scope=*)           SCOPE="${1#*=}"; shift ;;
    --with-mcp)          WITH_MCP=true; shift ;;
    --non-interactive)   NON_INTERACTIVE=true; shift ;;
    --list-runtimes)     list_runtimes; exit 0 ;;
    -h|--help)           usage; exit 0 ;;
    --)                  shift; break ;;
    *)                   die "Unknown flag: '$1'. Try --help." ;;
  esac
done

# --- Preflight --------------------------------------------------------------

if [[ -z "${HOME:-}" ]]; then
  die "HOME is not set. Cannot locate config directory."
fi

case "$(uname -s)" in
  Darwin)  : ;;   # macOS — native
  Linux)   : ;;   # Linux / WSL — supported
  MINGW*|MSYS*|CYGWIN*)
    die "Windows native shell detected. pm-agent-harness-kit requires a Unix-like environment. \
Install WSL (Windows Subsystem for Linux) and run this installer from your WSL terminal."
    ;;
  *) die "Unsupported OS: $(uname -s). See manual install in the README." ;;
esac

if ! has curl; then die "curl is required. Install it and re-run."; fi
if ! has tar;  then die "tar is required. Install it and re-run."; fi

# --- Resolve runtime (interactive vs. silent) -------------------------------

if [[ -z "$RUNTIME" ]]; then
  if $NON_INTERACTIVE; then
    die "No runtime specified. Use --runtime <id> or TPM_TOOLS_RUNTIME=<id>."
  fi
  # ── Interactive TUI ──
  VER="$(cat "${BASH_SOURCE%/*}/../VERSION" 2>/dev/null || echo "?")"

  # Header
  printf "\n  ${MAGENTA}${BOLD}pm-agent-harness-kit${RESET} ${DIM}v${VER}${RESET}\n"
  printf "  ${DIM}7 specialized PM agents · 59 skills${RESET}\n"
  printf "  ${DIM}pm-lead → explorer → strategist → builder → reviewer${RESET}\n\n"

  # Step 1 — Runtime
  printf "  ${BOLD}▸ AI Runtime${RESET}\n"
  printf "  ${CYAN}1)${RESET} opencode      ${DIM}(default)${RESET}\n"
  printf "  ${CYAN}2)${RESET} claude-code\n"
  printf "  ${CYAN}3)${RESET} copilot       ${DIM}(planned)${RESET}\n"
  printf "  ${CYAN}4)${RESET} codex         ${DIM}(planned)${RESET}\n\n"
  while true; do
    read -r -p "  Choice [1]: " choice < /dev/tty
    choice="${choice:-1}"
    case "$choice" in
      1) RUNTIME="opencode"; break ;;
      2) RUNTIME="claude-code"; break ;;
      3) RUNTIME="copilot"; break ;;
      4) RUNTIME="codex"; break ;;
      *) printf "  ${YELLOW}Invalid. Enter 1-4.${RESET}\n" ;;
    esac
  done

  # Copilot/Codex compliance note
  case "$RUNTIME" in
    copilot|codex)
      printf "\n  ${YELLOW}'${RUNTIME}' is planned — files install but runtime integration\n"
      printf "  is not complete.${RESET}\n\n"
      read -r -p "  Continue anyway? (y/N) " confirm < /dev/tty
      [[ "$confirm" =~ ^[Yy] ]] || { printf "  ${DIM}Cancelled.${RESET}\n"; exit 0; }
      ;;
  esac

  # Step 2 — Scope
  printf "\n  ${BOLD}▸ Scope${RESET}\n"
  printf "  ${CYAN}g)${RESET} global ${DIM}(all projects — default)${RESET}\n"
  printf "  ${CYAN}p)${RESET} this project only ${DIM}(.opencode/)${RESET}\n\n"
  read -r -p "  Choice [g]: " scope_choice < /dev/tty
  case "${scope_choice:-g}" in
    p|P|project) SCOPE="project" ;;
    *)           SCOPE="global" ;;
  esac

  # Step 3 — Path (scope-aware)
  case "$RUNTIME" in
    opencode)
      case "$SCOPE" in
        project) DEFAULT_DIR="$(pwd)/.opencode" ;;
        *)       DEFAULT_DIR="$HOME/.config/opencode" ;;
      esac ;;
    claude-code)
      case "$SCOPE" in
        project) DEFAULT_DIR="$(pwd)/.claude" ;;
        *)       DEFAULT_DIR="$HOME/.claude" ;;
      esac ;;
    copilot)
      case "$SCOPE" in
        project) DEFAULT_DIR="$(pwd)/.github/copilot" ;;
        *)       DEFAULT_DIR="$HOME/.github/copilot" ;;
      esac ;;
    codex)
      case "$SCOPE" in
        project) DEFAULT_DIR="$(pwd)/.codex" ;;
        *)       DEFAULT_DIR="$HOME/.codex" ;;
      esac ;;
  esac
  printf "\n  ${BOLD}▸ Install path${RESET}\n"
  read -r -p "  [${DEFAULT_DIR}]: " config_input < /dev/tty
  OC_ROOT="${config_input:-$DEFAULT_DIR}"

  # Step 4 — Summary
  printf "\n  ${BOLD}▸ Summary${RESET}\n"
  printf "  ${DIM}Runtime:${RESET}     ${CYAN}${RUNTIME}${RESET}\n"
  printf "  ${DIM}Scope:${RESET}       ${CYAN}${SCOPE}${RESET}\n"
  printf "  ${DIM}Install to:${RESET}  ${CYAN}${OC_ROOT}${RESET}\n"
  printf "  ${DIM}Skills:${RESET}      59\n"
  printf "  ${DIM}Agents:${RESET}      7  ${DIM}(4 in Tab, 3 subagent-only)${RESET}\n"
  printf "  ${DIM}Updates:${RESET}     ${GREEN}pm-lead checks on startup${RESET}\n\n"
  read -r -p "  Proceed? (Y/n) " confirm < /dev/tty
  if [[ "$confirm" =~ ^[Nn] ]]; then
    printf "  ${DIM}Cancelled.${RESET}\n"
    exit 0
  fi
  printf "\n"

else
  # ── Silent mode (runtime specified) ──
  SCOPE="${SCOPE:-global}"
  OC_ROOT="${OPENCODE_CONFIG_DIR:-}"
  if [[ -z "$OC_ROOT" ]]; then
    case "$SCOPE" in
      project)
        case "$RUNTIME" in
          opencode)    OC_ROOT="$(pwd)/.opencode" ;;
          claude-code) OC_ROOT="$(pwd)/.claude" ;;
          copilot)     OC_ROOT="$(pwd)/.github/copilot" ;;
          codex)       OC_ROOT="$(pwd)/.codex" ;;
          *)           die "Unknown runtime: '$RUNTIME'." ;;
        esac ;;
      *)
        case "$RUNTIME" in
          opencode)    OC_ROOT="$HOME/.config/opencode" ;;
          claude-code) OC_ROOT="$HOME/.claude" ;;
          copilot)     OC_ROOT="$HOME/.github/copilot" ;;
          codex)       OC_ROOT="$HOME/.codex" ;;
          *)           die "Unknown runtime: '$RUNTIME'. Use --list-runtimes." ;;
        esac ;;
    esac
  fi
fi

# --- Runtime configuration --------------------------------------------------

case "$RUNTIME" in
  opencode)
    SKILL_DIR="$OC_ROOT/skills"
    AGENT_DIR="$OC_ROOT/agents"
    VERSION_FILE="$OC_ROOT/pm-ahk.version"
    UPDATE_FLAG="$OC_ROOT/pm-ahk.update-available"
    BINARY_NAME="opencode"
    BINARY_URL="https://opencode.ai"
    VERIFY_HINT="Press Tab → select 'pm-lead'"
    ;;
  claude-code)
    SKILL_DIR="$OC_ROOT/skills"
    AGENT_DIR="$OC_ROOT/agents"
    VERSION_FILE="$OC_ROOT/pm-ahk.version"
    UPDATE_FLAG="$OC_ROOT/pm-ahk.update-available"
    BINARY_NAME="claude"
    BINARY_URL="https://docs.anthropic.com/en/docs/claude-code"
    VERIFY_HINT="In Claude Code, run '/agent pm-lead'"
    ;;
  copilot)
    SKILL_DIR="$OC_ROOT/instructions"
    AGENT_DIR="$OC_ROOT/prompts"
    VERSION_FILE="$OC_ROOT/pm-ahk.version"
    UPDATE_FLAG="$OC_ROOT/pm-ahk.update-available"
    BINARY_NAME=""
    BINARY_URL=""
    VERIFY_HINT="Copilot loads prompts from $AGENT_DIR/"
    ;;
  codex)
    SKILL_DIR="$OC_ROOT/skills"
    AGENT_DIR="$OC_ROOT/agents"
    VERSION_FILE="$OC_ROOT/pm-ahk.version"
    UPDATE_FLAG="$OC_ROOT/pm-ahk.update-available"
    BINARY_NAME=""
    BINARY_URL=""
    VERIFY_HINT="Codex loads agents from $AGENT_DIR/"
    ;;
esac

cyan "Installing pm-agent-harness-kit for runtime '$RUNTIME'"

# --- Soft binary check ------------------------------------------------------

if [[ -n "$BINARY_NAME" ]] && ! has "$BINARY_NAME"; then
  yellow "  warning: '$BINARY_NAME' not found on PATH."
  yellow "           Files will still be installed; install from $BINARY_URL to use them."
fi

# --- Download archive -------------------------------------------------------

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cyan "  Downloading..."
curl -fsSL "$ARCHIVE_URL" -o "$tmp_dir/repo.tar.gz" \
  || die "Failed to download from $ARCHIVE_URL"

tar xzf "$tmp_dir/repo.tar.gz" -C "$tmp_dir" || die "Failed to extract."

# Find extraction directory
EXTRACTED_DIR="$tmp_dir/pm-agent-harness-kit-${BRANCH}"
if [[ ! -d "$EXTRACTED_DIR" ]]; then
  EXTRACTED_DIR="$tmp_dir/$(ls "$tmp_dir" | grep -v 'repo.tar.gz' | head -1)"
fi
if [[ ! -d "$EXTRACTED_DIR" ]]; then
  die "Extraction failed — expected directory not found."
fi

mkdir -p "$SKILL_DIR" "$AGENT_DIR"

# --- Clean old backups from previous installs ---------------------------------

cyan "  Cleaning old backups..."
OLD_BACKUPS=0
for d in "$SKILL_DIR" "$AGENT_DIR"; do
  if [[ -d "$d" ]]; then
    for bak in "$d/"*.bak.*; do
      [[ -e "$bak" ]] || continue
      rm -rf "$bak"
      OLD_BACKUPS=$((OLD_BACKUPS + 1))
    done
  fi
done
[[ $OLD_BACKUPS -gt 0 ]] && dim "  Removed $OLD_BACKUPS old backup files"

backup_path() {
  local src="$1"
  if [[ -e "$src" ]]; then
    # Remove any previous backups of this same file
    rm -rf "${src}.bak."* 2>/dev/null || true
    local bak="${src}.bak.$(date +%s)"
    mv "$src" "$bak"
    dim "  Backed up: $src"
  fi
}

# --- Install skills ---------------------------------------------------------

cyan "  Installing 59 skills..."
mkdir -p "$SKILL_DIR"

if [[ -d "$EXTRACTED_DIR/skills" ]]; then
  for skill_dir in "$EXTRACTED_DIR/skills"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    target="$SKILL_DIR/$skill_name"
    backup_path "$target"
    cp -r "$skill_dir" "$target"
    SKILL_COUNT=$((SKILL_COUNT + 1))
  done
  green "  Skills: $SKILL_COUNT installed"
else
  die "No skills/ directory found in the archive."
fi

# --- Install agents (transformed for target runtime) ------------------------

cyan "  Installing 7 agents..."
mkdir -p "$AGENT_DIR"

# Remove old monolithic tpm.md if it exists
backup_path "$AGENT_DIR/tpm.md"

AGENT_TRANSFORMER="$EXTRACTED_DIR/scripts/transform-frontmatter.sh"

agent_count=0
for agent_file in "$EXTRACTED_DIR/agents"/*.md; do
  agent_name="$(basename "$agent_file")"
  [[ "$agent_name" == "README.md" ]] && continue
  [[ "$agent_name" == *.archived ]] && continue

  target="$AGENT_DIR/$agent_name"
  backup_path "$target"

  # Transform via canonical → runtime format
  if [[ -f "$AGENT_TRANSFORMER" ]]; then
    bash "$AGENT_TRANSFORMER" "$agent_file" --runtime "$RUNTIME" > "$target"
  else
    # Fallback: copy as-is (opencode format)
    cp "$agent_file" "$target"
  fi
  agent_count=$((agent_count + 1))
done

green "  Agents: $agent_count installed (transformed for $RUNTIME)"

# --- Claude Code: settings.json ---------------------------------------------

if [[ "$RUNTIME" == "claude-code" ]]; then
  SETTINGS_FILE="$OC_ROOT/settings.json"
  if [[ -f "$SETTINGS_FILE" ]] && grep -q '"agent"' "$SETTINGS_FILE" 2>/dev/null; then
    yellow "  settings.json already has an 'agent' setting — not overwriting."
  else
    backup_path "$SETTINGS_FILE"
    cat > "$SETTINGS_FILE" <<- 'CFG'
{
  "agent": "pm-lead",
  "skills": {
    "sources": [
      {
        "type": "file",
        "path": "{{config_dir}}/skills/*/SKILL.md"
      }
    ]
  }
}
CFG
    green "  settings.json created: $SETTINGS_FILE"
  fi
fi

# --- Install daily check script ---------------------------------------------

CRON_SOURCE="$EXTRACTED_DIR/scripts/pm-ahk-cron.sh"
CRON_TARGET="$OC_ROOT/pm-ahk-cron.sh"
if [[ -f "$CRON_SOURCE" ]]; then
  cp "$CRON_SOURCE" "$CRON_TARGET"
  chmod +x "$CRON_TARGET"
  # Run it once to set the initial update flag
  bash "$CRON_TARGET" 2>/dev/null || true
  dim "  Update checker installed: $CRON_TARGET"
fi

# --- Store version ----------------------------------------------------------

echo "$(cat "$EXTRACTED_DIR/VERSION" 2>/dev/null || echo 'unknown')" > "$VERSION_FILE"
FILE_VERSION="$(cat "$VERSION_FILE")"
green "  Version: $FILE_VERSION"

# --- MCP Harness (Phase 5) ---------------------------------------------------

if $WITH_MCP; then
  if has python3; then
    PY_VER="$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d. -f1)"
    if [[ "$PY_VER" -ge 3 ]]; then
      # Copy MCP scripts
      mkdir -p "$OC_ROOT"
      cp "$EXTRACTED_DIR/scripts/pm-ahk.py" "$OC_ROOT/pm-ahk.py"
      cp "$EXTRACTED_DIR/scripts/pm-ahk" "$OC_ROOT/pm-ahk"
      chmod +x "$OC_ROOT/pm-ahk" "$OC_ROOT/pm-ahk.py"

      # Copy dashboard dist/
      if [[ -d "$EXTRACTED_DIR/dashboard/dist" ]]; then
        mkdir -p "$OC_ROOT/pm-ahk-dashboard"
        cp -r "$EXTRACTED_DIR/dashboard/dist/"* "$OC_ROOT/pm-ahk-dashboard/"
      fi

      # Initialize harness (quiet — config snippet not needed, install handles it)
      python3 "$OC_ROOT/pm-ahk.py" init --scope "$SCOPE" 2>&1 >/dev/null

      # Register MCP server in opencode.json (stdio, type: local)
      if [[ "$RUNTIME" == "opencode" && -f "$OC_ROOT/opencode.json" ]]; then
        python3 <<- PYEOF
import json
cfg = json.load(open("${OC_ROOT}/opencode.json"))
cfg.setdefault("mcp", {})["pm-ahk"] = {
    "type": "local",
    "command": ["python3", "-u", "${OC_ROOT}/pm-ahk.py", "serve"],
    "enabled": True
}
json.dump(cfg, open("${OC_ROOT}/opencode.json", "w"), indent=2)
PYEOF
        green "  MCP server registered (stdio, auto-started by opencode)"
      fi

      # Register MCP server for Claude Code (~/.claude.json)
      if [[ "$RUNTIME" == "claude-code" || ! -f "$OC_ROOT/opencode.json" ]]; then
        python3 <<- PYEOF
import json, os
path = os.path.expanduser("~/.claude.json")
cfg = json.load(open(path)) if os.path.exists(path) else {}
cfg.setdefault("mcpServers", {})["pm-ahk"] = {
    "command": "python3",
    "args": ["-u", "${OC_ROOT}/pm-ahk.py", "serve"]
}
json.dump(cfg, open(path, "w"), indent=2)
PYEOF
        green "  MCP server registered for Claude Code"
      fi

      green "  MCP harness installed (stdio — auto-started by AI runtime)"
    else
    yellow "  Python 3.8+ required for MCP harness. Found: $(python3 --version 2>/dev/null || echo 'not found')"
    fi
  else
    yellow "  Python 3 not found. MCP harness requires Python 3.12+."
    yellow "  Install from https://python.org and re-run with --with-mcp"
  fi
fi

# --- Post-install -----------------------------------------------------------

echo ""
box_top
box_title "  pm-agent-harness-kit installed!"
box_line ""
box_line "  Runtime:     $RUNTIME"
box_line "  Scope:       $SCOPE"
box_line "  Skills:      $SKILL_COUNT"
box_line "  Agents:      $agent_count  (5 in Tab, 2 subagent-only)"
box_line "  Version:     $FILE_VERSION"
box_bot
echo ""
echo "  ${BOLD}Next:${RESET}"
echo "    1. Restart $BINARY_NAME (if it was running)"
echo "    2. $VERIFY_HINT"
echo "    3. Ask pm-lead anything — it classifies and routes to specialist agents."
echo ""


# Project-scope gitignore hint
if [[ "$SCOPE" == "project" ]]; then
  yellow "  ⚠ Project-local install. Add to .gitignore:"
  yellow "    .opencode/"
  echo ""
fi

echo "  ${BOLD}Try:${RESET}"
echo "    \"Write a PRD for checkout v2\""
echo "    \"Research our churn problem\""
echo "    \"Am I ready for a Director role?\""
echo ""

# Show update hint if flag exists
if [[ -f "$UPDATE_FLAG" ]]; then
  NEW_VER="$(cat "$UPDATE_FLAG")"
  yellow "  A newer version ($NEW_VER) is available."
  yellow "  Run: curl -fsSL $BASE_URL/update.sh | bash"
  echo ""
fi

# Windows note
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    yellow "  Note: Native Windows is not supported. Run from WSL."
    echo ""
    ;;
esac

dim "  To check for updates: curl -fsSL $BASE_URL/scripts/check-update.sh | bash"
dim "  To uninstall:         curl -fsSL $BASE_URL/uninstall.sh | TPM_TOOLS_RUNTIME=$RUNTIME bash"
echo ""

