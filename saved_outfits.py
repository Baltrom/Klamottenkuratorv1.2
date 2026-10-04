"""Gespeicherte Outfits des Klamotten Kurators ("Save outfit").

Ein gespeichertes Outfit ist ein dict mit den Feldern
Outfit_ID ("O001"), Items (Slot -> Clothing_ID oder None), Season, Occasion,
Edgy (bool), Anchor (Clothing_ID oder None) und Saved (Datum, ISO).
Gespeichert werden nur IDs. Wird ein Teil später gelöscht, bleibt das Outfit erhalten
und zeigt das Teil als "(deleted)" (siehe resolve_outfit).
"""

import json
from datetime import date
from pathlib import Path

from wardrobe import (OCCASIONS, SEASONS, ClothingDataError, data_dir,
                      save_wardrobe)


SAVED_NAME = "saved_outfits.json"
DEFAULT_SAVED_PATH = data_dir() / SAVED_NAME

DELETED_NAME = "(deleted)"


class SavedOutfitError(ClothingDataError):
    """Die Datei mit den gespeicherten Outfits ist kaputt oder enthält ungültige Einträge."""


def _validate(record, position):
    label = record.get("Outfit_ID", f"entry #{position}") if isinstance(record, dict) else f"entry #{position}"
    if not isinstance(record, dict):
        raise SavedOutfitError(f"Saved outfit #{position}: expected an object.")
    for key in ("Outfit_ID", "Items", "Season", "Occasion", "Edgy", "Anchor", "Saved"):
        if key not in record:
            raise SavedOutfitError(f"Saved outfit {label}: missing field '{key}'.")
    if not isinstance(record["Items"], dict):
        raise SavedOutfitError(f"Saved outfit {label}: 'Items' must be an object.")
    if record["Season"] not in SEASONS:
        raise SavedOutfitError(f"Saved outfit {label}: unknown Season '{record['Season']}'.")
    if record["Occasion"] not in OCCASIONS:
        raise SavedOutfitError(f"Saved outfit {label}: unknown Occasion '{record['Occasion']}'.")


def load_saved(path=DEFAULT_SAVED_PATH):
    """Liest die gespeicherten Outfits. Eine fehlende Datei ist eine leere Liste."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
    except json.JSONDecodeError as e:
        raise SavedOutfitError(f"Saved outfits file is not valid JSON ({path.name}, line {e.lineno}): {e.msg}") from None
    if not isinstance(records, list):
        raise SavedOutfitError(f"{path.name}: top level must be a list.")
    for position, record in enumerate(records, start=1):
        _validate(record, position)
    return records


def next_outfit_id(records):
    numbers = [int(r["Outfit_ID"][1:]) for r in records if str(r["Outfit_ID"])[1:].isdigit()]
    return f"O{max(numbers, default=0) + 1:03d}"


def save_outfit(records, outfit, season, occasion, anchor_id=None, path=DEFAULT_SAVED_PATH):
    """Speichert ein Outfit (Ergebnis von suggest_outfit) und schreibt die Datei (path=None: nur Speicher).

    Wirft ValueError, wenn genau dieses Outfit (gleiche Teile, Season, Occasion, Edgy) schon gespeichert ist.
    Gibt den neuen Eintrag zurück.
    """
    items = {slot: (item["Clothing_ID"] if item else None) for slot, item in outfit.slots.items()}
    for r in records:
        if (r["Items"] == items and r["Season"] == season and r["Occasion"] == occasion
                and r["Edgy"] == outfit.edgy):
            raise ValueError(f"This outfit is already saved ({r['Outfit_ID']}).")
    record = {
        "Outfit_ID": next_outfit_id(records),
        "Items": items,
        "Season": season,
        "Occasion": occasion,
        "Edgy": bool(outfit.edgy),
        "Anchor": anchor_id,
        "Saved": date.today().isoformat(),
    }
    _validate(record, len(records) + 1)
    records.append(record)
    if path is not None:
        try:
            save_wardrobe(records, path)
        except BaseException:
            records.pop()
            raise
    return record


def delete_saved(records, outfit_id, path=DEFAULT_SAVED_PATH):
    """Löscht ein gespeichertes Outfit. Wirft ValueError bei unbekannter ID."""
    index = next((i for i, r in enumerate(records) if r["Outfit_ID"] == outfit_id), None)
    if index is None:
        raise ValueError(f"Unknown Outfit_ID '{outfit_id}'.")
    removed = records.pop(index)
    if path is not None:
        try:
            save_wardrobe(records, path)
        except BaseException:
            records.insert(index, removed)
            raise
    return removed


def resolve_outfit(record, wardrobe):
    """Schlägt die Teile eines gespeicherten Outfits im Kleiderschrank nach.

    Gibt (slots, has_deleted) zurück. slots: Slot -> Kleidungsstück (dict), None (kein Teil)
    oder ein Platzhalter {"Clothing_ID": ..., "Name": "(deleted)", "deleted": True}
    für ein inzwischen gelöschtes Teil.
    """
    by_id = {i["Clothing_ID"]: i for i in wardrobe}
    slots, has_deleted = {}, False
    for slot, clothing_id in record["Items"].items():
        if clothing_id is None:
            slots[slot] = None
        elif clothing_id in by_id:
            slots[slot] = by_id[clothing_id]
        else:
            slots[slot] = {"Clothing_ID": clothing_id, "Name": DELETED_NAME, "deleted": True}
            has_deleted = True
    return slots, has_deleted
