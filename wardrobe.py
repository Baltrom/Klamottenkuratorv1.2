"""Datenschicht des Klamotten Kurators.

Enthält die erlaubten Werte (für Validierung und GUI-Buttons) sowie Laden,
Speichern, Hinzufügen, Ändern und Löschen von Kleidungsstücken in der JSON-Flatfile.
Ein Kleidungsstück ist ein dict mit den Feldern
Clothing_ID, Name, Color, Occasion (Liste), Category, Subcategory, Season (Liste).
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

DATASET_NAME = "clothing_curator_dataset.json"
APP_NAME = "Klamottenkurator"


def _is_frozen():
    """True, wenn das Programm als .exe (PyInstaller) läuft."""
    return bool(getattr(sys, "frozen", False))


def bundled_dir():
    """Ordner mit den mitgelieferten, nur lesbaren Dateien (Datenbasis)."""
    if _is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).parent


def data_dir():
    """Ordner mit den veränderbaren Nutzerdaten (Kleiderschrank, gespeicherte Outfits).

    Als .exe: der Ordner Klamottenkurator in %APPDATA%, damit jeder Nutzer seinen eigenen Schrank hat und
    Daten Neustarts und neue Programmversionen überleben (NFR3). Entwicklung: der Projektordner.
    Mit der Umgebungsvariable KLAMOTTENKURATOR_DATA lässt sich der Ordner überschreiben.
    """
    override = os.environ.get("KLAMOTTENKURATOR_DATA")
    if override:
        return Path(override)
    if _is_frozen():
        base = os.environ.get("APPDATA") or Path.home()
        return Path(base) / APP_NAME
    return Path(__file__).parent


DEFAULT_PATH = data_dir() / DATASET_NAME


def ensure_user_data(path=DEFAULT_PATH):
    """Legt beim ersten Start den Nutzerordner an und kopiert die mitgelieferte Datenbasis hinein.

    Eine vorhandene Datei wird nie überschrieben. Fehlt auch die mitgelieferte Datei, passiert nichts
    (load_wardrobe meldet dann 'file not found').
    """
    path = Path(path)
    if path.exists():
        return
    seed = bundled_dir() / DATASET_NAME
    if seed.exists() and seed.resolve() != path.resolve():
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed, path)

SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
OCCASIONS = ["Casual", "Formal", "Sport"]

# Kategorie -> Unterkategorien (für die Button-Auswahl in der GUI).
SUBCATEGORIES = {
    "Top": ["T-Shirt", "Polo Shirt", "Tank Top", "Long Sleeve Top", "Shirt", "Hoodie", "Sweater"],
    "Bottom": ["Jeans", "Trousers", "Chinos", "Cargo Pants", "Sweatpants", "Shorts", "Athletic Shorts"],
    "Footwear": ["Sneakers", "Running Shoes", "Boots", "Loafers"],
    "Socks": ["Ankle Socks", "Crew Socks", "Wool Socks"],
    "Outerwear": ["Bomber Jacket", "Denim Jacket", "Jacket", "Rain Jacket", "Parka", "Suit Jacket"],
    "Headwear": ["Baseball Cap", "Beanie", "Bucket Hat"],
}
CATEGORIES = list(SUBCATEGORIES)

# Farbpalette: jede Farbe ist entweder neutral oder hat einen Farbton (Grad im Farbrad).
# Eine neue Farbe muss hier eingeordnet werden, sonst lehnt der Loader sie ab.
NEUTRAL_COLORS = {"White", "Black", "Grey", "Beige", "Cream", "Navy", "Brown"}
COLOR_HUES = {"Blue": 215, "Light Blue": 200, "Olive Green": 75, "Burgundy": 345}
COLORS = ["White", "Black", "Grey", "Beige", "Cream", "Navy", "Brown",
          "Blue", "Light Blue", "Olive Green", "Burgundy"]
assert set(COLORS) == NEUTRAL_COLORS | set(COLOR_HUES)

REQUIRED_FIELDS = ("Clothing_ID", "Name", "Color", "Occasion", "Category", "Subcategory", "Season")


class ClothingDataError(Exception):
    """Die Kleiderschrank-Datei fehlt, ist kaputt oder enthält ungültige Einträge."""


def _validate_item(item, position, seen_ids):
    """Prüft ein Kleidungsstück und wirft ClothingDataError mit verständlicher Meldung."""
    if not isinstance(item, dict):
        raise ClothingDataError(f"Entry #{position}: expected an object, got {type(item).__name__}.")
    label = item.get("Clothing_ID", f"entry #{position}")

    missing = [f for f in REQUIRED_FIELDS if f not in item]
    if missing:
        raise ClothingDataError(f"Item {label}: missing field(s) {', '.join(missing)}.")

    for field in ("Clothing_ID", "Name", "Color", "Category", "Subcategory"):
        if not isinstance(item[field], str) or not item[field].strip():
            raise ClothingDataError(f"Item {label}: '{field}' must be a non-empty text.")
    if item["Clothing_ID"] in seen_ids:
        raise ClothingDataError(f"Duplicate Clothing_ID {item['Clothing_ID']}.")
    if item["Color"] not in COLORS:
        raise ClothingDataError(f"Item {label}: unknown Color '{item['Color']}'. Allowed: {', '.join(COLORS)}.")
    if item["Category"] not in CATEGORIES:
        raise ClothingDataError(f"Item {label}: unknown Category '{item['Category']}'. Allowed: {', '.join(CATEGORIES)}.")

    for field, allowed in (("Season", SEASONS), ("Occasion", OCCASIONS)):
        values = item[field]
        if not isinstance(values, list) or not values:
            raise ClothingDataError(f"Item {label}: '{field}' must be a non-empty list.")
        unknown = [v for v in values if v not in allowed]
        if unknown:
            raise ClothingDataError(f"Item {label}: unknown {field} {unknown}. Allowed: {', '.join(allowed)}.")


def load_wardrobe(path=DEFAULT_PATH):
    """Liest den Kleiderschrank aus der JSON-Datei und gibt eine Liste von dicts zurück.

    Eine leere Liste ist ein gültiger (leerer) Kleiderschrank.
    Wirft ClothingDataError bei fehlender Datei, kaputtem JSON oder ungültigen Einträgen.
    """
    path = Path(path)
    if path == DEFAULT_PATH:
        ensure_user_data(path)
    try:
        with open(path, encoding="utf-8") as f:
            items = json.load(f)
    except FileNotFoundError:
        raise ClothingDataError(f"Wardrobe file not found: {path}") from None
    except json.JSONDecodeError as e:
        raise ClothingDataError(f"Wardrobe file is not valid JSON ({path.name}, line {e.lineno}): {e.msg}") from None

    if not isinstance(items, list):
        raise ClothingDataError(f"{path.name}: top level must be a list of clothing items.")

    seen_ids = set()
    for position, item in enumerate(items, start=1):
        _validate_item(item, position, seen_ids)
        seen_ids.add(item["Clothing_ID"])
    return items


def save_wardrobe(items, path=DEFAULT_PATH):
    """Schreibt den Kleiderschrank atomar: erst in eine Temp-Datei, dann ersetzen.

    So bleibt die alte Datei heil, falls das Programm mitten im Schreiben abbricht (NFR3).
    """
    path = Path(path)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.stem, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def next_id(items):
    """Nächste freie ID im Format C046 (höchste vorhandene Nummer + 1)."""
    numbers = [int(i["Clothing_ID"][1:]) for i in items
               if i["Clothing_ID"][1:].isdigit()]
    return f"C{max(numbers, default=0) + 1:03d}"


def add_item(items, category, subcategory, color, occasions, seasons, name=None, path=DEFAULT_PATH):
    """Fügt ein Kleidungsstück hinzu und speichert die Datei (path=None: nur im Speicher).

    Gedacht für die Button-Auswahl: category, subcategory, color einzeln,
    occasions und seasons als Liste der gewählten Buttons.
    Ohne name wird "<Color> <Subcategory>" verwendet. Gibt das neue Item zurück.
    """
    item = {
        "Clothing_ID": next_id(items),
        "Name": name or f"{color} {subcategory}",
        "Color": color,
        "Occasion": list(occasions),
        "Category": category,
        "Subcategory": subcategory,
        "Season": [s for s in SEASONS if s in seasons],  # feste Reihenfolge
    }
    _validate_item(item, len(items) + 1, {i["Clothing_ID"] for i in items})
    items.append(item)
    if path is not None:
        try:
            save_wardrobe(items, path)
        except BaseException:
            items.pop()  # Speicher und Datei sollen nicht auseinanderlaufen
            raise
    return item


def _find_index(items, clothing_id):
    for index, item in enumerate(items):
        if item["Clothing_ID"] == clothing_id:
            return index
    raise ValueError(f"Unknown Clothing_ID '{clothing_id}'.")


def update_item(items, clothing_id, *, name=None, category=None, subcategory=None, color=None,
                occasions=None, seasons=None, path=DEFAULT_PATH):
    """Ändert Felder eines Kleidungsstücks und speichert die Datei (path=None: nur im Speicher).

    Nur die übergebenen Felder werden geändert, die Clothing_ID bleibt gleich.
    Ungültige Werte werfen ClothingDataError, dann bleibt alles unverändert.
    Gibt das geänderte Item zurück. Wirft ValueError bei unbekannter ID.
    """
    index = _find_index(items, clothing_id)
    old = items[index]
    new = dict(old)
    for key, value in (("Name", name), ("Category", category), ("Subcategory", subcategory),
                       ("Color", color)):
        if value is not None:
            new[key] = value
    if occasions is not None:
        new["Occasion"] = list(occasions)
    if seasons is not None:
        new["Season"] = [s for s in SEASONS if s in seasons]  # feste Reihenfolge
    _validate_item(new, index + 1, {i["Clothing_ID"] for i in items} - {clothing_id})
    items[index] = new
    if path is not None:
        try:
            save_wardrobe(items, path)
        except BaseException:
            items[index] = old  # Speicher und Datei sollen nicht auseinanderlaufen
            raise
    return new


def delete_item(items, clothing_id, path=DEFAULT_PATH):
    """Löscht ein Kleidungsstück und speichert die Datei (path=None: nur im Speicher).

    Die IDs der übrigen Teile bleiben unverändert. Gibt das gelöschte Item zurück.
    Wirft ValueError bei unbekannter ID.
    """
    index = _find_index(items, clothing_id)
    removed = items.pop(index)
    if path is not None:
        try:
            save_wardrobe(items, path)
        except BaseException:
            items.insert(index, removed)
            raise
    return removed
