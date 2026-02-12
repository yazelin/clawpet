"""CLI for clawpet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clawpet.core import (
    PROFILE_PATH,
    adopt_pet,
    build_prompt,
    get_pet,
    interact,
    list_pets,
    load_profile,
    save_profile,
)


def _profile_path(raw: str | None) -> Path | None:
    return Path(raw).expanduser() if raw else None


def _print_json(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_pets(args: argparse.Namespace) -> int:
    pets = []
    for entry in list_pets():
        pet = get_pet(entry["id"])
        profile = pet["profile"]
        pets.append(
            {
                "id": pet["id"],
                "name_zh": profile["name_zh"],
                "name_en": profile["name_en"],
                "species": pet["species"],
                "summary": profile["summary"],
            }
        )

    if args.json:
        _print_json(pets)
        return 0

    for pet in pets:
        print(f"- {pet['id']:<9} [{pet['species']}] {pet['name_zh']} / {pet['name_en']} — {pet['summary']}")
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
    profile = load_profile(path)
    pet = get_pet(profile["adopted_pet_id"])
    payload = {"pet": pet["profile"], "species": pet["species"], "state": profile["state"], "updated_at": profile["updated_at"]}

    if args.json:
        _print_json(payload)
        return 0

    state = profile["state"]
    print(f"Current pet: {pet['profile']['name_zh']} / {pet['profile']['name_en']} ({pet['species']})")
    print(f"Mood: {state['mood']}, Energy: {state['energy']}, Hunger: {state['hunger']}, Bond: {state['bond']}")
    print(f"Updated: {profile['updated_at']}")
    return 0


def cmd_interact(args: argparse.Namespace) -> int:
    path = _profile_path(args.profile)
    profile = load_profile(path)
    updated = interact(profile, args.action)
    save_profile(updated, path)
    pet = get_pet(updated["adopted_pet_id"])

    if args.json:
        _print_json({"action": args.action, "pet": pet["profile"], "state": updated["state"]})
        return 0

    state = updated["state"]
    print(f"Action: {args.action}")
    print(f"Pet: {pet['profile']['name_zh']} / {pet['profile']['name_en']}")
    print(f"State -> Mood: {state['mood']}, Energy: {state['energy']}, Hunger: {state['hunger']}, Bond: {state['bond']}")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    if args.pet_id:
        pet = get_pet(args.pet_id)
        state = pet["state_defaults"]
    else:
        profile = load_profile(_profile_path(args.profile))
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
        "prompt": prompt,
    }

    if args.json:
        _print_json(payload)
        return 0

    print(prompt)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clawpet", description="OpenClaw pet companion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pets_parser = subparsers.add_parser("pets", help="List available pets")
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

    prompt_parser = subparsers.add_parser("prompt", help="Generate image prompt text for the pet")
    prompt_parser.add_argument("--pet-id", help="Use a specific pet id instead of profile")
    prompt_parser.add_argument("--mood", help="Override mood text")
    prompt_parser.add_argument("--place", default="a warm room with soft afternoon light", help="Scene location")
    prompt_parser.add_argument("--style", default="illustration", help="Visual style")
    prompt_parser.add_argument("--profile", help="Profile file path")
    prompt_parser.add_argument("--json", action="store_true", help="Output JSON")
    prompt_parser.set_defaults(func=cmd_prompt)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

