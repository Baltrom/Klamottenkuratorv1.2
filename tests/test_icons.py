import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

pytest.importorskip("PySide6")
import icons
import wardrobe


def test_every_category_has_a_icon():
    assert set(icons.SHAPES) == set(wardrobe.CATEGORIES)


@pytest.mark.parametrize("category", list(icons.SHAPES))
def test_icon_fits_the_grid_and_is_not_empty(category):
    filled, detail = icons.cells(category)
    assert 30 < len(filled) < icons.SIZE * icons.SIZE
    assert detail <= filled
    # eine Zelle Rand bleibt für den Umriss frei
    assert all(1 <= r <= icons.SIZE - 2 and 1 <= c <= icons.SIZE - 2 for r, c in filled)


def test_logo_grid_is_square():
    assert len(icons.LOGO) == icons.SIZE and all(len(row) == icons.SIZE for row in icons.LOGO)
