#!/usr/bin/env bash
# pm-agent-harness-kit uninstaller — removes the agent and all skills installed by install.sh
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/uninstall.sh | bash
#   ./uninstall.sh --runtime opencode
#   ./uninstall.sh --list-runtimes

set -euo pipefail

REPO="DIAL-Studio/pm-agent-harness-kit"
RUNTIME="${TPM_TOOLS_RUNTIME:-opencode}"
SCOPE="${TPM_TOOLS_SCOPE:-global}"

green()  { printf "\033[32m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*"; }
cyan()   { printf "\033[36m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
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
pm-agent-harness-kit uninstaller

Usage:
  ./uninstall.sh --runtime <id>
  ./uninstall.sh --runtime <id> --scope project
  curl -fsSL .../uninstall.sh | TPM_TOOLS_RUNTIME=opencode bash
EOF
      exit 0 ;;
    *) die "Unknown flag: '$1'." ;;
  esac
done

[[ -n "${HOME:-}" ]] || die "HOME is not set."

case "$RUNTIME" in
  opencode)
    if [[ "$SCOPE" == "project" ]]; then
      OC_ROOT="${OPENCODE_CONFIG_DIR:-$(pwd)/.opencode}"
    else
      OC_ROOT="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"
    fi
    SKILL_DIR="$OC_ROOT/skills"
    AGENT_DIR="$OC_ROOT/agents"
    VERSION_FILE="$OC_ROOT/pm-ahk.version"
    CONFIG_SNIPPET="$OC_ROOT/opencode-pm-agent-harness-kit.json"
    SKILL_NAMES=(
      acquisition-channel-advisor agent-orchestration-advisor
      ai-shaped-readiness-advisor altitude-horizon-framework
      business-health-diagnostic company-intel company-research
      context-engineering-advisor customer-journey-map
      customer-journey-mapping-workshop derisk-measurement-advisor
      director-readiness-advisor discovery-interview-prep discovery-process
      eol-message epic-breakdown-advisor epic-hypothesis
      executive-onboarding-playbook experiment-designer
      feature-investment-advisor finance-based-pricing-advisor
      finance-metrics-quickref growth-plg-advisor jobs-to-be-done
      lean-ux-canvas opportunity-solution-tree organic-growth-advisor
      pestel-analysis pm-skill-creator pol-probe-advisor pol-probe positioning-statement
      positioning-workshop prd-development press-release prioritization-advisor
      problem-framing-canvas problem-statement product-sense-interview-answer
      product-strategy-session proto-persona recommendation-canvas
      roadmap-planning       saas-economics-efficiency-metrics
      saas-revenue-growth-metrics skill-authoring-workflow stakeholder-engagement-advisor
      stakeholder-identification stakeholder-mapping storyboard
      strategy-canvas tam-sam-som-calculator tpm-artifacts user-story
      user-story-mapping user-story-mapping-workshop user-story-splitting
      vp-cpo-readiness-advisor workshop-facilitation
    )
    TARGETS=()
    # All 7 PM-AHK agents + old tpm.md fallback
    for agent in pm-lead pm-explorer pm-strategist pm-builder pm-reviewer pm-coach pm-smith tpm; do
      TARGETS+=("$AGENT_DIR/${agent}.md")
    done
    for name in "${SKILL_NAMES[@]}"; do
      TARGETS+=("$SKILL_DIR/$name")
    done
    TARGETS+=("$VERSION_FILE")
    TARGETS+=("$CONFIG_SNIPPET")
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

count_removed=0
for t in "${TARGETS[@]}"; do
  if [[ -e "$t" ]]; then
    rm -rf "$t"
    green "Removed: $t"
    count_removed=$((count_removed + 1))
  fi
done

if [[ $count_removed -eq 0 ]]; then
  yellow "Nothing to remove."
else
  green "Removed $count_removed items."
fi

green "Restart '$RUNTIME' to reflect the change."
green "Done."
