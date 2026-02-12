#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
SKILL_NAME="clawpet"
SKILLS_DIR="$OPENCLAW_DIR/skills"
SKILL_DEST="$SKILLS_DIR/$SKILL_NAME"
OPENCLAW_CONFIG="$OPENCLAW_DIR/openclaw.json"
WORKSPACE_DIR="$OPENCLAW_DIR/workspace"
SOUL_MD="$WORKSPACE_DIR/SOUL.md"
SOUL_TEMPLATE="$ROOT_DIR/templates/soul-injection.md"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required. Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

mkdir -p "$SKILLS_DIR" "$WORKSPACE_DIR"

echo "[1/4] Installing clawpet CLI with uv..."
uv tool install --from "$ROOT_DIR" clawpet --force

echo "[2/4] Installing OpenClaw skill files..."
mkdir -p "$SKILL_DEST"
cp "$ROOT_DIR/skill/SKILL.md" "$SKILL_DEST/SKILL.md"

echo "[3/4] Updating OpenClaw config..."
python3 - "$OPENCLAW_CONFIG" "$SKILLS_DIR" "$SKILL_NAME" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
skills_dir = sys.argv[2]
skill_name = sys.argv[3]

if config_path.exists():
    data = json.loads(config_path.read_text(encoding="utf-8"))
else:
    data = {}

skills = data.setdefault("skills", {})
entries = skills.setdefault("entries", {})
entry = entries.setdefault(skill_name, {})
entry["enabled"] = True

load = skills.setdefault("load", {})
extra_dirs = load.setdefault("extraDirs", [])
if skills_dir not in extra_dirs:
    extra_dirs.append(skills_dir)

config_path.parent.mkdir(parents=True, exist_ok=True)
config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "[4/4] Injecting SOUL capability..."
if [ ! -f "$SOUL_MD" ]; then
  printf "# Agent Soul\n\n" > "$SOUL_MD"
fi
if ! grep -q "## Clawpet Companion Capability" "$SOUL_MD"; then
  printf "\n%s\n" "$(cat "$SOUL_TEMPLATE")" >> "$SOUL_MD"
fi

echo
echo "Done. Try:"
echo "  clawpet pets"
echo "  clawpet adopt momo"
echo "  clawpet status"

