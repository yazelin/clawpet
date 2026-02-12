from pathlib import Path

from datetime import datetime, timezone

from clawpet.core import (
    adopt_pet,
    apply_passive_decay,
    auto_care_action,
    build_prompt,
    build_snapshot_url,
    get_pet,
    interact,
    list_pets,
    load_profile,
    parse_catime_entries,
)


def test_list_pets_includes_four_cats():
    pets = list_pets()
    ids = {pet["id"] for pet in pets}
    assert {"momo", "mochi", "captain", "lingling"}.issubset(ids)
    assert "bunny-scout" not in ids


def test_list_pets_all_includes_disabled_species():
    pets = list_pets(enabled_only=False)
    ids = {pet["id"] for pet in pets}
    assert "bunny-scout" in ids


def test_adopt_and_load_profile(tmp_path: Path):
    profile_file = tmp_path / "profile.json"
    adopt_pet("momo", profile_file)
    profile = load_profile(profile_file)
    assert profile["adopted_pet_id"] == "momo"
    assert profile["state"]["mood"] >= 0


def test_interact_feed_lowers_hunger(tmp_path: Path):
    profile_file = tmp_path / "profile.json"
    profile = adopt_pet("mochi", profile_file)
    before = profile["state"]["hunger"]
    after = interact(profile, "feed")
    assert after["state"]["hunger"] <= before


def test_prompt_contains_pet_name():
    pet = get_pet("lingling")
    prompt = build_prompt(pet, pet["state_defaults"], place="a flower shop", style="soft watercolor")
    assert "Lingling" in prompt
    assert "flower shop" in prompt


def test_parse_catime_entries():
    sample = """Cat # 241  2026-02-11 04:57 UTC  model: gemini-3-pro-image-preview
  URL: https://example.com/cat.webp
  Idea: 一隻可愛貓咪
  Prompt: A cute cat
  Story: 一個溫暖故事
"""
    parsed = parse_catime_entries(sample)
    assert len(parsed) == 1
    assert parsed[0]["number"] == 241
    assert parsed[0]["url"] == "https://example.com/cat.webp"


def test_passive_decay_changes_state_when_time_elapsed():
    profile = {
        "adopted_pet_id": "momo",
        "state": {"mood": 80, "energy": 80, "hunger": 20, "bond": 50},
        "updated_at": "2026-02-12 00:00 UTC",
    }
    now = datetime(2026, 2, 12, 3, 0, tzinfo=timezone.utc)
    refreshed, elapsed = apply_passive_decay(profile, now)
    assert elapsed == 3
    assert refreshed["state"]["hunger"] == 32
    assert refreshed["state"]["energy"] == 71
    assert refreshed["state"]["mood"] == 74
    assert refreshed["state"]["bond"] == 47


def test_auto_care_action_picks_expected_action():
    assert auto_care_action({"hunger": 80, "energy": 80, "mood": 50, "bond": 40}) == "feed"
    assert auto_care_action({"hunger": 40, "energy": 20, "mood": 50, "bond": 40}) == "rest"
    assert auto_care_action({"hunger": 40, "energy": 60, "mood": 50, "bond": 40}) == "play"


def test_build_snapshot_url_returns_http_url():
    url = build_snapshot_url("A cat playing with a red ball")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "A%20cat%20playing%20with%20a%20red%20ball" in url
    assert "model=flux" in url
