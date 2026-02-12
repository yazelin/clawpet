# Copilot Instructions for `clawpet`

## Build, test, and lint commands

- Install dev dependencies: `uv sync --extra dev`
- Run full test suite: `uv run pytest -q`
- Run a single test: `uv run pytest tests/test_core.py::test_parse_catime_entries -q`
- Build package artifacts: `uv build` (Hatchling backend from `pyproject.toml`)
- Install local CLI (used by local installer flow): `uv tool install --from . clawpet --force`
- No lint command is currently configured in this repository.

## High-level architecture

- CLI entrypoint is `src/clawpet/cli.py` (`clawpet = clawpet.cli:main`), implemented as `argparse` subcommands with `cmd_*` handlers that return exit codes.
- Core behavior is in `src/clawpet/core.py`:
  - pet catalog loading (`list_pets`, `get_pet`) via `importlib.resources`
  - profile lifecycle (`load_profile`, `save_profile`, `adopt_pet`)
  - state transitions (`interact`, `auto_care_action`, passive decay)
  - output helpers (`build_prompt`, `build_snapshot_url`, `parse_catime_entries`)
- Pet content is data-driven under `src/clawpet/data/pets/`:
  - `index.json` controls `default_pet`, per-pet file mapping, species, and `enabled` visibility
  - `<id>.json` stores profile/appearance/personality/default-state/prompt data
  - package data is force-included via `[tool.hatch.build.targets.wheel.force-include]`
- OpenClaw integration surfaces:
  - `skill/SKILL.md` defines how agents should invoke the skill
  - `skill/scripts/clawpet.sh` wraps execution with fallback order:
    1) local `clawpet`
    2) `uvx --from git+https://github.com/yazelin/clawpet.git clawpet ...`
    3) `uv tool run --from git+https://github.com/yazelin/clawpet.git clawpet ...`
  - `scripts/install_local.sh` installs CLI + skill, updates `~/.openclaw/openclaw.json`, and injects template content into `~/.openclaw/workspace/SOUL.md`

## Key conventions in this codebase

- Keep the pet state schema fixed to `mood`, `energy`, `hunger`, `bond`; values are clamped to `0..100`.
- Default profile path is `~/.openclaw/clawpet/profile.json`; `--profile` is the standard override path for CLI commands.
- Commands that depend on current state should use the live-profile flow (`_load_live_profile`) so passive decay is applied before action logic.
- Preserve `--json` output behavior for CLI commands; skill/agent flows rely on machine-readable responses.
- For image flows, use `snapshot --json` and pass returned `image_url` (HTTP/HTTPS), not local filesystem paths.
- For new pet entries, follow JSON-first extension:
  1) add item in `pets/index.json`
  2) add matching `pets/<id>.json`
  3) use `enabled: false` for species/examples not ready for default listing
