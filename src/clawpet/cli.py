"""CLI for clawpet."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from clawpet.core import (
    PROFILE_PATH,
    adopt_pet,
    apply_passive_decay,
    auto_care_action,
    build_prompt,
    get_pet,
    interact,
    list_pets,
    load_profile,
    parse_catime_entries,
    save_profile,
)


def _profile_path(raw: str | None) -> Path | None:
    return Path(raw).expanduser() if raw else None


def _print_json(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _load_live_profile(path: Path | None) -> tuple[dict, int]:
    profile = load_profile(path)
    refreshed, elapsed_hours = apply_passive_decay(profile)
    if elapsed_hours > 0:
        save_profile(refreshed, path)
    return refreshed, elapsed_hours


def cmd_pets(args: argparse.Namespace) -> int:
    pets = []
    for entry in list_pets(enabled_only=not args.all):
        pet = get_pet(entry["id"])
        profile = pet["profile"]
        pets.append(
            {
                "id": pet["id"],
                "name_zh": profile["name_zh"],
                "name_en": profile["name_en"],
                "species": pet["species"],
                "enabled": entry.get("enabled", True),
                "summary": profile["summary"],
            }
        )

    if args.json:
        _print_json(pets)
        return 0

    for pet in pets:
        status = "enabled" if pet["enabled"] else "disabled"
        print(
            f"- {pet['id']:<12} [{pet['species']}] ({status}) "
            f"{pet['name_zh']} / {pet['name_en']} — {pet['summary']}"
        )
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    pet = get_pet(args.pet_id)
    if args.json:
        _print_json(pet)
        return 0

    profile = pet["profile"]
    print(f"{profile['name_zh']} / {profile['name_en']} ({pet['id']})")
    print(f"Species: {pet['species']}")
    print(f"Summary: {profile['summary']}")
    print(f"Traits: {', '.join(pet['personality']['traits'])}")
    print(f"Favorite places: {', '.join(pet['personality']['favorite_places'])}")
    return 0


def cmd_adopt(args: argparse.Namespace) -> int:
    path = _profile_path(args.profile)
    profile = adopt_pet(args.pet_id, path)
    pet = get_pet(profile["adopted_pet_id"])

    if args.json:
        _print_json({"profile": profile, "pet": pet["profile"]})
        return 0

    print(f"Adopted: {pet['profile']['name_zh']} / {pet['profile']['name_en']}")
    print(f"Profile file: {(path or PROFILE_PATH)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    path = _profile_path(args.profile)
    profile, elapsed_hours = _load_live_profile(path)
    pet = get_pet(profile["adopted_pet_id"])
    payload = {
        "pet": pet["profile"],
        "species": pet["species"],
        "state": profile["state"],
        "updated_at": profile["updated_at"],
        "elapsed_hours": elapsed_hours,
    }

    if args.json:
        _print_json(payload)
        return 0

    state = profile["state"]
    print(f"Current pet: {pet['profile']['name_zh']} / {pet['profile']['name_en']} ({pet['species']})")
    print(f"Mood: {state['mood']}, Energy: {state['energy']}, Hunger: {state['hunger']}, Bond: {state['bond']}")
    if elapsed_hours > 0:
        print(f"Passive update applied: {elapsed_hours}h elapsed")
    print(f"Updated: {profile['updated_at']}")
    return 0


def cmd_interact(args: argparse.Namespace) -> int:
    path = _profile_path(args.profile)
    profile, elapsed_hours = _load_live_profile(path)
    updated = interact(profile, args.action)
    save_profile(updated, path)
    pet = get_pet(updated["adopted_pet_id"])

    if args.json:
        _print_json({"action": args.action, "pet": pet["profile"], "state": updated["state"]})
        return 0

    state = updated["state"]
    if elapsed_hours > 0:
        print(f"Passive update applied first: {elapsed_hours}h elapsed")
    print(f"Action: {args.action}")
    print(f"Pet: {pet['profile']['name_zh']} / {pet['profile']['name_en']}")
    print(f"State -> Mood: {state['mood']}, Energy: {state['energy']}, Hunger: {state['hunger']}, Bond: {state['bond']}")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    if args.pet_id:
        pet = get_pet(args.pet_id)
        state = pet["state_defaults"]
        elapsed_hours = 0
    else:
        profile_path = _profile_path(args.profile)
        profile, elapsed_hours = _load_live_profile(profile_path)
        pet = get_pet(profile["adopted_pet_id"])
        state = profile["state"]

    prompt = build_prompt(
        pet,
        state,
        mood=args.mood,
        place=args.place,
        style=args.style,
    )

    payload = {
        "pet_id": pet["id"],
        "pet_name": f"{pet['profile']['name_zh']} / {pet['profile']['name_en']}",
        "species": pet["species"],
        "elapsed_hours": elapsed_hours,
        "prompt": prompt,
    }

    if args.json:
        _print_json(payload)
        return 0

    print(prompt)
    return 0


def cmd_care(args: argparse.Namespace) -> int:
    path = _profile_path(args.profile)
    profile, elapsed_hours = _load_live_profile(path)
    chosen_action = args.action or auto_care_action(profile["state"])
    updated = interact(profile, chosen_action)
    save_profile(updated, path)
    pet = get_pet(updated["adopted_pet_id"])

    payload = {
        "pet": pet["profile"],
        "action": chosen_action,
        "elapsed_hours": elapsed_hours,
        "state": updated["state"],
    }
    if args.json:
        _print_json(payload)
        return 0

    if elapsed_hours > 0:
        print(f"Passive update applied first: {elapsed_hours}h elapsed")
    print(f"Auto care action: {chosen_action}")
    print(f"Pet: {pet['profile']['name_zh']} / {pet['profile']['name_en']}")
    state = updated["state"]
    print(f"State -> Mood: {state['mood']}, Energy: {state['energy']}, Hunger: {state['hunger']}, Bond: {state['bond']}")
    return 0


def cmd_catime(args: argparse.Namespace) -> int:
    if shutil.which("catime") is None:
        print("Error: catime CLI not found. Install it first (e.g. pip install catime).", file=sys.stderr)
        return 2

    query = args.query or "latest"
    command = ["catime", query]
    if args.repo:
        command.extend(["--repo", args.repo])

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip() or "catime command failed"
        print(f"Error: {error_text}", file=sys.stderr)
        return result.returncode

    entries = parse_catime_entries(result.stdout)
    selected = entries[-1] if entries else None
    payload = {
        "query": query,
        "count": len(entries),
        "selected": selected,
        "entries": entries,
    }

    if args.json:
        _print_json(payload)
        return 0

    if not selected:
        print("No cat entries parsed from catime output.")
        return 1

    print(f"Catime query: {query}")
    print(f"Selected cat #{selected['number']} at {selected['timestamp']}")
    print(f"URL: {selected.get('url', 'N/A')}")
    if selected.get("story"):
        print(f"Story: {selected['story']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clawpet", description="OpenClaw pet companion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pets_parser = subparsers.add_parser("pets", help="List available pets")
    pets_parser.add_argument("--all", action="store_true", help="Include disabled pets")
    pets_parser.add_argument("--json", action="store_true", help="Output JSON")
    pets_parser.set_defaults(func=cmd_pets)

    show_parser = subparsers.add_parser("show", help="Show one pet profile")
    show_parser.add_argument("pet_id", help="Pet id")
    show_parser.add_argument("--json", action="store_true", help="Output JSON")
    show_parser.set_defaults(func=cmd_show)

    adopt_parser = subparsers.add_parser("adopt", help="Adopt a pet")
    adopt_parser.add_argument("pet_id", help="Pet id")
    adopt_parser.add_argument("--profile", help="Profile file path")
    adopt_parser.add_argument("--json", action="store_true", help="Output JSON")
    adopt_parser.set_defaults(func=cmd_adopt)

    status_parser = subparsers.add_parser("status", help="Show current pet status")
    status_parser.add_argument("--profile", help="Profile file path")
    status_parser.add_argument("--json", action="store_true", help="Output JSON")
    status_parser.set_defaults(func=cmd_status)

    interact_parser = subparsers.add_parser("interact", help="Interact with current pet")
    interact_parser.add_argument("action", choices=["feed", "play", "rest"], help="Interaction action")
    interact_parser.add_argument("--profile", help="Profile file path")
    interact_parser.add_argument("--json", action="store_true", help="Output JSON")
    interact_parser.set_defaults(func=cmd_interact)

    care_parser = subparsers.add_parser("care", help="Auto-care current pet based on status")
    care_parser.add_argument("--action", choices=["feed", "play", "rest"], help="Override auto action")
    care_parser.add_argument("--profile", help="Profile file path")
    care_parser.add_argument("--json", action="store_true", help="Output JSON")
    care_parser.set_defaults(func=cmd_care)

    prompt_parser = subparsers.add_parser("prompt", help="Generate image prompt text for the pet")
    prompt_parser.add_argument("--pet-id", help="Use a specific pet id instead of profile")
    prompt_parser.add_argument("--mood", help="Override mood text")
    prompt_parser.add_argument("--place", default="a warm room with soft afternoon light", help="Scene location")
    prompt_parser.add_argument("--style", default="illustration", help="Visual style")
    prompt_parser.add_argument("--profile", help="Profile file path")
    prompt_parser.add_argument("--json", action="store_true", help="Output JSON")
    prompt_parser.set_defaults(func=cmd_prompt)

    catime_parser = subparsers.add_parser("catime", help="Parse catime CLI output in a clawpet-friendly format")
    catime_parser.add_argument("query", nargs="?", default="latest", help="catime query, e.g. latest, today, 42")
    catime_parser.add_argument("--repo", help="Optional catime --repo override")
    catime_parser.add_argument("--json", action="store_true", help="Output JSON")
    catime_parser.set_defaults(func=cmd_catime)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
