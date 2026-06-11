#!/usr/bin/env bash
# Syncs the official ElevenLabs skills (github.com/elevenlabs/skills, MIT)
# into this plugin's skills/ directory. Copies ONLY the allowlisted folders;
# gap skills authored in this repo are never touched.
set -euo pipefail

REPO_URL="https://github.com/elevenlabs/skills"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$PLUGIN_DIR/skills"
VENDORED=(agents music setup-api-key sound-effects speech-engine speech-to-text text-to-speech voice-changer voice-isolator)

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Cloning $REPO_URL ..."
git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR/upstream"

missing=()
for skill in "${VENDORED[@]}"; do
  [[ -d "$TMP_DIR/upstream/$skill" && -f "$TMP_DIR/upstream/$skill/SKILL.md" ]] || missing+=("$skill")
done
if (( ${#missing[@]} > 0 )); then
  echo "ERROR: upstream is missing expected skill folders (or their SKILL.md): ${missing[*]}" >&2
  echo "Upstream may have restructured. Nothing was changed locally." >&2
  echo "Update the VENDORED allowlist in this script to match upstream." >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"
for skill in "${VENDORED[@]}"; do
  rsync -a --delete "$TMP_DIR/upstream/$skill/" "$SKILLS_DIR/$skill/"
done

echo "Synced ${#VENDORED[@]} skills from $REPO_URL"
echo "Local changes (empty means already up to date):"
git -C "$PLUGIN_DIR" status --short -- skills/
