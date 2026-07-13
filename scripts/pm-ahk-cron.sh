#!/usr/bin/env bash
# pm-ahk-cron.sh — silent daily update check for pm-agent-harness-kit.
#
# Checks the remote VERSION once a day and writes a flag file if an update
# is available. pm-lead reads this flag on startup and notifies the user.
#
# No notifications. No pop-ups. No output unless there's an error.
#
# Install (launchd — macOS):
#   cp pm-ahk-cron.sh ~/.config/opencode/
#   cat > ~/Library/LaunchAgents/com.pm-ahk.update-check.plist << EOF
#   <?xml version="1.0" encoding="UTF-8"?>
#   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
#   <plist version="1.0">
#   <dict>
#     <key>Label</key><string>com.pm-ahk.update-check</string>
#     <key>ProgramArguments</key><array><string>~/.config/opencode/pm-ahk-cron.sh</string></array>
#     <key>StartInterval</key><integer>86400</integer>
#     <key>RunAtLoad</key><true/>
#   </dict>
#   </plist>
#   EOF
#   launchctl load ~/Library/LaunchAgents/com.pm-ahk.update-check.plist
#
# Install (cron — Linux/WSL):
#   (crontab -l 2>/dev/null; echo "0 10 * * * ~/.config/opencode/pm-ahk-cron.sh") | crontab -
#
# This script also runs during install.sh to set up the flag for first use.

set -euo pipefail

# Try all possible config paths: global opencode, project-local opencode, claude-code
OC_GLOBAL="$HOME/.config/opencode"
OC_PROJECT="$(pwd)/.opencode"
CC_GLOBAL="$HOME/.claude"
CC_PROJECT="$(pwd)/.claude"

LOCAL_VERSION_FILE=""
REMOTE_VERSION_URL="https://raw.githubusercontent.com/DIAL-Studio/pm-agent-harness-kit/main/VERSION"
UPDATE_FLAG=""

for dir in "$OC_GLOBAL" "$OC_PROJECT" "$CC_GLOBAL" "$CC_PROJECT"; do
  if [[ -f "$dir/pm-ahk.version" ]]; then
    LOCAL_VERSION_FILE="$dir/pm-ahk.version"
    UPDATE_FLAG="$dir/pm-ahk.update-available"
    break
  fi
done

LOCAL_VERSION="$(cat "$LOCAL_VERSION_FILE" | tr -d '[:space:]')"
REMOTE_VERSION="$(curl -fsSL --connect-timeout 5 "$REMOTE_VERSION_URL" 2>/dev/null | tr -d '[:space:]' || true)"

if [[ -z "$REMOTE_VERSION" ]]; then
  # Network unavailable — exit silently
  exit 0
fi

if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
  # Update available — write flag
  echo "$REMOTE_VERSION" > "$UPDATE_FLAG"
else
  # Up to date — remove flag if it exists
  rm -f "$UPDATE_FLAG"
fi

exit 0
