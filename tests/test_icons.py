import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

pytest.importorskip("PySide6")
import icons
import wardrobe


def test_every_subcategory_has_an_icon():
    names = {s for subs in wardrobe.SUBCATEGORIES.values() for s in subs}
    assert names == set(icons.ICONS)


def test_category_defaults_exist():
    assert set(icons.CATEGORY_DEFAULT) == set(wardrobe.CATEGORIES)
    assert all(name in icons.ICONS for name in icons.CATEGORY_DEFAULT.values())
    assert icons.resolve("Unknown Thing", "Footwear") == icons.CATEGORY_DEFAULT["Footwear"]


@pytest.mark.parametrize("name", list(icons.ICONS))
def test_icon_fits_and_uses_known_symbols(name):
    g = icons.grid(name)
    assert len(g) == icons.SIZE and all(len(row) == icons.SIZE for row in g)
    used = set("".join(g)) - {"."}
    assert len("".join(g).replace(".", "")) > 150
    allowed = set(icons.PANELS) | set("rx12345f") | set(icons.FIXED)
    assert used <= allowed, used - allowed
    for row in icons.shades(name):
        for v in row:
            assert v is None or v in (1, 2, 3, 4, 5) or v in icons.FIXED


def test_logo_grid_is_square():
    assert len(icons.LOGO) == 16 and all(len(row) == 16 for row in icons.LOGO)
