"""Core logic for clawpet."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

PROFILE_PATH = Path.home() / ".openclaw" / "clawpet" / "profile.json"
PETS_PACKAGE = "clawpet.data.pets"

INTERACTION_DELTAS = {
    "feed": {"hunger": -20, "mood": 6, "bond": 4, "energy": 2},
    "play": {"hunger": 10, "mood": 14, "bond": 7, "energy": -12},
    "rest": {"hunger": 6, "mood": 5, "bond": 2, "energy": 18},
}

CATIME_HEADER_RE = re.compile(r"^Cat #\s*(\d+)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)\s+model:\s*(.+)$")
PROFILE_TIME_FORMAT = "%Y-%m-%d %H:%M UTC"
PASSIVE_DELTAS_PER_HOUR = {"hunger": 4, "energy": -3, "mood": -2, "bond": -1}
MAX_PASSIVE_HOURS = 72


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime(PROFILE_TIME_FORMAT)


def _parse_utc(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, PROFILE_TIME_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _read_resource_json(filename: str) -> dict:
    resource = resources.files(PETS_PACKAGE).joinpath(filename)
    with resource.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pet_index() -> dict:
    return _read_resource_json("index.json")


def list_pets(*, enabled_only: bool = True) -> list[dict]:
    records = pet_index().get("pets", [])
    if enabled_only:
        return [record for record in records if record.get("enabled", True)]
    return records


def get_pet(pet_id: str) -> dict:
    for entry in list_pets(enabled_only=False):
        if entry.get("id") == pet_id:
            detail = _read_resource_json(entry["file"])
            detail["id"] = entry["id"]
            detail["species"] = entry.get("species", detail.get("profile", {}).get("species", "unknown"))
            return detail
    raise KeyError(f"Unknown pet id: {pet_id}")


def _clamp(value: int) -> int:
    return max(0, min(100, int(value)))


def default_state(pet: dict) -> dict:
    defaults = pet.get("state_defaults", {})
    return {
        "mood": _clamp(defaults.get("mood", 70)),
        "energy": _clamp(defaults.get("energy", 70)),
        "hunger": _clamp(defaults.get("hunger", 30)),
        "bond": _clamp(defaults.get("bond", 35)),
    }


def _normalize_state(raw_state: dict | None, defaults: dict) -> dict:
    source = raw_state or {}
    return {
        "mood": _clamp(source.get("mood", defaults["mood"])),
        "energy": _clamp(source.get("energy", defaults["energy"])),
        "hunger": _clamp(source.get("hunger", defaults["hunger"])),
        "bond": _clamp(source.get("bond", defaults["bond"])),
    }


def _default_pet_id() -> str:
    return pet_index().get("default_pet", "momo")


def initial_profile(pet_id: str | None = None) -> dict:
    chosen_id = pet_id or _default_pet_id()
    pet = get_pet(chosen_id)
    return {
        "adopted_pet_id": chosen_id,
        "state": default_state(pet),
        "updated_at": _utc_now(),
    }


def load_profile(profile_path: Path | None = None) -> dict:
    path = profile_path or PROFILE_PATH
    if not path.exists():
        return initial_profile()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in profile: {path}") from exc

    adopted_pet_id = payload.get("adopted_pet_id") or _default_pet_id()
    pet = get_pet(adopted_pet_id)
    defaults = default_state(pet)
    state = _normalize_state(payload.get("state"), defaults)
    return {
        "adopted_pet_id": pet["id"],
        "state": state,
        "updated_at": payload.get("updated_at") or _utc_now(),
    }


def save_profile(profile: dict, profile_path: Path | None = None) -> Path:
    path = profile_path or PROFILE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def adopt_pet(pet_id: str, profile_path: Path | None = None) -> dict:
    pet = get_pet(pet_id)
    profile = {
        "adopted_pet_id": pet["id"],
        "state": default_state(pet),
        "updated_at": _utc_now(),
    }
    save_profile(profile, profile_path)
    return profile


def interact(profile: dict, action: str) -> dict:
    if action not in INTERACTION_DELTAS:
        raise ValueError(f"Unsupported action: {action}")

    state = dict(profile["state"])
    for field, delta in INTERACTION_DELTAS[action].items():
        state[field] = _clamp(state[field] + delta)

    return {
        "adopted_pet_id": profile["adopted_pet_id"],
        "state": state,
        "updated_at": _utc_now(),
    }


def apply_passive_decay(profile: dict, now: datetime | None = None) -> tuple[dict, int]:
    """Apply passive state changes based on elapsed hours since last update."""
    current_time = now or datetime.now(timezone.utc)
    updated_at = _parse_utc(profile.get("updated_at", ""))
    if updated_at is None:
        source = profile.get("state", {})
        normalized = {
            "adopted_pet_id": profile["adopted_pet_id"],
            "state": {
                "mood": _clamp(source.get("mood", 70)),
                "energy": _clamp(source.get("energy", 70)),
                "hunger": _clamp(source.get("hunger", 30)),
                "bond": _clamp(source.get("bond", 35)),
            },
            "updated_at": current_time.strftime(PROFILE_TIME_FORMAT),
        }
        return normalized, 0

    elapsed_hours = int((current_time - updated_at).total_seconds() // 3600)
    if elapsed_hours <= 0:
        return profile, 0

    elapsed_hours = min(elapsed_hours, MAX_PASSIVE_HOURS)
    state = dict(profile["state"])
    for field, per_hour_delta in PASSIVE_DELTAS_PER_HOUR.items():
        state[field] = _clamp(state[field] + per_hour_delta * elapsed_hours)

    if state["hunger"] >= 85:
        state["mood"] = _clamp(state["mood"] - 6)

    refreshed = {
        "adopted_pet_id": profile["adopted_pet_id"],
        "state": state,
        "updated_at": current_time.strftime(PROFILE_TIME_FORMAT),
    }
    return refreshed, elapsed_hours


def mood_label(score: int) -> str:
    if score >= 85:
        return "very happy"
    if score >= 65:
        return "happy"
    if score >= 40:
        return "calm"
    return "sleepy"


def suggest_activity(state: dict) -> str:
    if state["energy"] <= 30:
        return "curling up for a cozy nap"
    if state["hunger"] >= 75:
        return "looking around for snacks"
    if state["bond"] >= 80:
        return "staying close to the user and asking for cuddles"
    return "playing with a favorite toy"


def auto_care_action(state: dict) -> str:
    if state["hunger"] >= 70:
        return "feed"
    if state["energy"] <= 35:
        return "rest"
    return "play"


def build_prompt(
    pet: dict,
    state: dict,
    *,
    mood: str | None = None,
    place: str = "a warm room with soft afternoon light",
    style: str = "illustration",
) -> str:
    profile = pet["profile"]
    appearance = pet["appearance"]
    emotion = mood or mood_label(state["mood"])
    activity = suggest_activity(state)
    return (
        f"{profile['name_en']} ({profile['name_zh']}), a {appearance['breed']}, is {activity} at {place}. "
        f"The pet feels {emotion}. Visual identity details: {pet['prompt_snippet']}. "
        f"Style: {style}, high coherence, wholesome companion vibe."
    )


def parse_catime_entries(stdout: str) -> list[dict]:
    """Parse `catime` CLI stdout into structured entries."""
    entries: list[dict] = []
    current: dict | None = None

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        header = CATIME_HEADER_RE.match(line)
        if header:
            if current:
                entries.append(current)
            current = {
                "number": int(header.group(1)),
                "timestamp": header.group(2),
                "model": header.group(3).strip(),
            }
            continue

        if current is None:
            continue

        if line.startswith("URL:"):
            current["url"] = line.removeprefix("URL:").strip()
        elif line.startswith("Idea:"):
            current["idea"] = line.removeprefix("Idea:").strip()
        elif line.startswith("Prompt:"):
            current["prompt"] = line.removeprefix("Prompt:").strip()
        elif line.startswith("Story:"):
            current["story"] = line.removeprefix("Story:").strip()

    if current:
        entries.append(current)

    return entries
