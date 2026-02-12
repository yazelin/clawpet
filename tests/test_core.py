from pathlib import Path

from clawpet.core import adopt_pet, build_prompt, get_pet, interact, list_pets, load_profile, parse_catime_entries


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
