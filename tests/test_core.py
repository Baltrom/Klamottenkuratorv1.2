import json
import random
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import outfit_engine as engine
import saved_outfits as so
import wardrobe as w


@pytest.fixture
def data(tmp_path):
    path = tmp_path / "wardrobe.json"
    shutil.copy(w.bundled_dir() / w.DATASET_NAME, path)
    return w.load_wardrobe(path), path


def test_update_and_delete(data):
    items, path = data
    n = len(items)
    w.update_item(items, "C001", color="Black", seasons=["Winter", "Spring"], path=path)
    assert w.load_wardrobe(path)[0]["Season"] == ["Spring", "Winter"]
    with pytest.raises(w.ClothingDataError):
        w.update_item(items, "C001", color="Pink", path=path)
    assert items[0]["Color"] == "Black"
    with pytest.raises(ValueError):
        w.delete_item(items, "C999", path=path)
    w.delete_item(items, "C002", path=path)
    assert len(w.load_wardrobe(path)) == n - 1


def test_ensure_user_data_copies_once(tmp_path, monkeypatch):
    target = tmp_path / "user" / w.DATASET_NAME
    w.ensure_user_data(target)
    assert target.exists()
    target.write_text("[]", encoding="utf-8")
    w.ensure_user_data(target)  # darf nichts überschreiben
    assert target.read_text(encoding="utf-8") == "[]"


def test_data_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("KLAMOTTENKURATOR_DATA", str(tmp_path))
    assert w.data_dir() == tmp_path


def test_engine_modes(data):
    items, _ = data
    rng = random.Random(1)
    with_anchor = engine.suggest_outfit(items, "C016", "Autumn", "Casual", rng=rng)
    assert with_anchor.slots["Bottom"]["Clothing_ID"] == "C016"
    free = engine.suggest_outfit(items, None, "Winter", "Formal", rng=rng)
    assert all(i is None or ("Winter" in i["Season"] and "Formal" in i["Occasion"]) for i in free.slots.values())
    edgy = engine.suggest_outfit(items, None, "Winter", "Casual", edgy=True, rng=rng)
    assert edgy.edgy and any(i and "Winter" not in i["Season"] for i in edgy.slots.values())
    with pytest.raises(ValueError):
        engine.suggest_outfit([], None, "Winter", "Casual")


def test_saved_outfits_roundtrip_and_deleted_item(data, tmp_path):
    items, _ = data
    saved_path = tmp_path / "saved.json"
    assert so.load_saved(saved_path) == []
    outfit = engine.suggest_outfit(items, "C016", "Autumn", "Casual", rng=random.Random(2))
    records = []
    rec = so.save_outfit(records, outfit, "Autumn", "Casual", "C016", path=saved_path)
    assert rec["Outfit_ID"] == "O001"
    assert so.load_saved(saved_path) == records
    with pytest.raises(ValueError):
        so.save_outfit(records, outfit, "Autumn", "Casual", "C016", path=saved_path)

    w.delete_item(items, "C016", path=None)
    slots, has_deleted = so.resolve_outfit(records[0], items)
    assert has_deleted and slots["Bottom"]["Name"] == "(deleted)"

    so.delete_saved(records, "O001", path=saved_path)
    assert so.load_saved(saved_path) == []


def test_broken_saved_file(tmp_path):
    p = tmp_path / "saved.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(so.SavedOutfitError):
        so.load_saved(p)


def test_anchor_is_always_used_without_warning(data):
    items, _ = data
    # C008 White Tank Top: nur Summer, Casual/Sport
    outfit = engine.suggest_outfit(items, "C008", "Winter", "Formal", rng=random.Random(3))
    assert outfit.slots["Top"]["Clothing_ID"] == "C008"
    assert not hasattr(outfit, "warnings")
    others = [i for s, i in outfit.slots.items() if i and s != "Top"]
    assert others and all("Winter" in i["Season"] and "Formal" in i["Occasion"] for i in others)


def test_suit_bonus(data):
    items, _ = data
    outfit = engine.suggest_outfit(items, "C056", "Autumn", "Formal", rng=random.Random(4))
    assert outfit.slots["Outerwear"]["Clothing_ID"] == "C056"
    assert outfit.slots["Bottom"]["Subcategory"] == "Trousers" and outfit.suit
    edgy = engine.suggest_outfit(items, "C056", "Autumn", "Formal", edgy=True, rng=random.Random(4))
    assert not edgy.suit
