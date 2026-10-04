"""Outfit-Algorithmus des Klamotten Kurators.

Ablauf (siehe Algorithmusbeschreibung):
1. Der Nutzer wählt ein Kleidungsstück (Ausgangsteil), eine Season und eine Occasion.
2. Pro Slot (Footwear, Socks, Bottom, Top, Outerwear) werden die Kandidaten geholt.
3. Unpassende Teile werden ausgeschlossen: Season UND Occasion müssen passen.
4. Die Kandidaten werden bewertet, die besten pro Slot kombiniert.
5. Jede Kombination erhält einen Kompatibilitätswert (0-100), gewichtet
   Season (50) > Occasion (30) > Color (20).
6. Ausgegeben wird ein Outfit; bei Gleichstand entscheidet der Zufall.
"""

import itertools
import random
from dataclasses import dataclass, field

from wardrobe import (COLOR_HUES, NEUTRAL_COLORS, OCCASIONS, SEASONS,
                      ClothingDataError, load_wardrobe)

SLOTS = ["Footwear", "Socks", "Bottom", "Top", "Outerwear"]
WEIGHTS = {"season": 50, "occasion": 30, "color": 20}

TOP_PER_SLOT = 8       # nur die besten Kandidaten je Slot werden kombiniert (Performance)
TIE_TOLERANCE = 3.0    # Outfits innerhalb dieser Punkte zum Besten gelten als gleich gut


# --- Einzelbewertungen (jeweils 0.0 bis 1.0) --------------------------------------

def season_fit(item, season):
    """0 wenn die Season nicht passt. Sonst höher, je spezialisierter das Teil ist
    (nur Summer = 1.0, alle vier Seasons = 0.25)."""
    if season not in item["Season"]:
        return 0.0
    return (len(SEASONS) + 1 - len(item["Season"])) / len(SEASONS)


def occasion_fit(item, occasion):
    """0 wenn die Occasion nicht passt. Sonst höher, je spezialisierter das Teil ist
    (nur Formal = 1.0, alle drei Occasions = 0.33)."""
    if occasion not in item["Occasion"]:
        return 0.0
    return (len(OCCASIONS) + 1 - len(item["Occasion"])) / len(OCCASIONS)


def color_harmony(color_a, color_b):
    """Einfache Farblehre für zwei Farben.

    neutral + neutral   1.0
    neutral + Farbe     0.9
    ähnlicher Farbton   0.85  (Abstand im Farbrad bis 45 Grad, inkl. gleiche Farbe)
    Kontrastfarben      0.8   (ab 120 Grad)
    sonst               0.4
    """
    a_neutral = color_a in NEUTRAL_COLORS
    b_neutral = color_b in NEUTRAL_COLORS
    if a_neutral and b_neutral:
        return 1.0
    if a_neutral or b_neutral:
        return 0.9
    diff = abs(COLOR_HUES[color_a] - COLOR_HUES[color_b])
    diff = min(diff, 360 - diff)
    if diff <= 45:
        return 0.85
    if diff >= 120:
        return 0.8
    return 0.4


def _outfit_color_harmony(items):
    """Durchschnitt der Farbharmonie über alle Paare des Outfits."""
    pairs = list(itertools.combinations(items, 2))
    if not pairs:
        return 1.0
    return sum(color_harmony(a["Color"], b["Color"]) for a, b in pairs) / len(pairs)


# --- Outfit -------------------------------------------------------------------------

@dataclass
class Outfit:
    slots: dict                 # Slot -> Kleidungsstück (dict) oder None, wenn nichts passt
    score: float                # Kompatibilitätswert 0-100
    season: float               # Teilwerte 0-1 (Durchschnitt bzw. Farbharmonie)
    occasion: float
    color: float
    warnings: list = field(default_factory=list)

    @property
    def key(self):
        """Identifiziert das Outfit über seine Teile (für 'anderes Outfit')."""
        return tuple(sorted(i["Clothing_ID"] for i in self.slots.values() if i))

    def format(self):
        """Textausgabe, eine Zeile je Slot."""
        lines = []
        for slot, item in self.slots.items():
            text = f"{item['Name']} ({item['Clothing_ID']})" if item else "- no suitable item in wardrobe"
            lines.append(f"{slot:<10} {text}")
        lines.append(f"Score      {self.score:.0f}/100  "
                     f"(season {self.season:.2f}, occasion {self.occasion:.2f}, color {self.color:.2f})")
        lines.extend(f"Note       {w}" for w in self.warnings)
        return "\n".join(lines)


def _score_outfit(slots, chosen, season, occasion):
    items = list(chosen.values())
    s = sum(season_fit(i, season) for i in items) / len(items)
    o = sum(occasion_fit(i, occasion) for i in items) / len(items)
    c = _outfit_color_harmony(items)
    score = WEIGHTS["season"] * s + WEIGHTS["occasion"] * o + WEIGHTS["color"] * c
    return Outfit({slot: chosen.get(slot) for slot in slots}, score, s, o, c)


def _candidates(wardrobe, slot, anchor, season, occasion):
    """Passende Teile für einen Slot, beste zuerst, höchstens TOP_PER_SLOT."""
    fitting = [i for i in wardrobe
               if i["Category"] == slot and i["Clothing_ID"] != anchor["Clothing_ID"]
               and season in i["Season"] and occasion in i["Occasion"]]

    def rating(item):
        return (WEIGHTS["season"] * season_fit(item, season)
                + WEIGHTS["occasion"] * occasion_fit(item, occasion)
                + WEIGHTS["color"] * color_harmony(item["Color"], anchor["Color"]))

    fitting.sort(key=lambda i: (-rating(i), i["Clothing_ID"]))
    return fitting[:TOP_PER_SLOT]


# --- Hauptfunktion ------------------------------------------------------------------

def suggest_outfit(wardrobe, anchor_id, season, occasion, *, exclude=(), rng=None):
    """Erstellt einen Outfitvorschlag rund um das Teil anchor_id.

    exclude: Outfit-Keys (Outfit.key) bereits gezeigter Outfits, für 'anderes Outfit'.
    rng:     optionaler random.Random für reproduzierbare Ergebnisse (Tests).
    Fehlt für einen Slot ein passendes Teil, bleibt der Slot None.
    Wirft ValueError bei unbekannter ID, Season oder Occasion.
    """
    if season not in SEASONS:
        raise ValueError(f"Unknown season '{season}'. Allowed: {', '.join(SEASONS)}.")
    if occasion not in OCCASIONS:
        raise ValueError(f"Unknown occasion '{occasion}'. Allowed: {', '.join(OCCASIONS)}.")
    anchor = next((i for i in wardrobe if i["Clothing_ID"] == anchor_id), None)
    if anchor is None:
        raise ValueError(f"Unknown Clothing_ID '{anchor_id}'.")

    warnings = []
    if season not in anchor["Season"]:
        warnings.append(f"{anchor['Name']} is not meant for {season}.")
    if occasion not in anchor["Occasion"]:
        warnings.append(f"{anchor['Name']} is not meant for {occasion}.")

    # Ist das Ausgangsteil eine Kopfbedeckung, wird sie zusätzlich ausgegeben.
    slots = (["Headwear"] if anchor["Category"] == "Headwear" else []) + SLOTS

    candidates = {}
    for slot in slots:
        if slot == anchor["Category"]:
            candidates[slot] = [anchor]
        else:
            candidates[slot] = _candidates(wardrobe, slot, anchor, season, occasion)

    filled = [s for s in slots if candidates[s]]
    outfits = []
    for combo in itertools.product(*(candidates[s] for s in filled)):
        outfit = _score_outfit(slots, dict(zip(filled, combo)), season, occasion)
        outfit.warnings = warnings
        outfits.append(outfit)

    excluded = set(exclude)
    pool = [o for o in outfits if o.key not in excluded] or outfits
    best = max(o.score for o in pool)
    top = [o for o in pool if o.score >= best - TIE_TOLERANCE]
    return (rng or random).choice(top)


# --- Kommandozeilen-Test ---------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Outfit suggestion from the command line (for testing).")
    parser.add_argument("clothing_id", help="e.g. C016")
    parser.add_argument("season", choices=SEASONS)
    parser.add_argument("occasion", choices=OCCASIONS)
    args = parser.parse_args()
    try:
        print(suggest_outfit(load_wardrobe(), args.clothing_id, args.season, args.occasion).format())
    except (ClothingDataError, ValueError) as e:
        parser.exit(1, f"Error: {e}\n")
