"""Rauchtest der Oberfläche (ohne Fenster, Qt-Plattform 'offscreen')."""
import os
import shutil
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def window(tmp_path, monkeypatch):
    monkeypatch.setenv("KLAMOTTENKURATOR_DATA", str(tmp_path))
    import importlib
    import saved_outfits
    import wardrobe
    importlib.reload(wardrobe)
    importlib.reload(saved_outfits)
    import gui
    importlib.reload(gui)
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    w = gui.MainWindow()
    yield w, gui
    w.deleteLater()


def test_first_start_copies_dataset_and_shows_items(window, tmp_path):
    w, _ = window
    assert (tmp_path / "clothing_curator_dataset.json").exists()
    assert len(w.wardrobe) == 55


def test_create_save_and_delete_outfit(window, tmp_path):
    w, _ = window
    w.create_outfit(new=True)
    assert w.current is not None
    w.save_current()
    assert len(w.saved) == 1 and (tmp_path / "saved_outfits.json").exists()
    w.create_outfit(new=False)
    w.save_current()
    assert len(w.saved) == 2
    w.delete_saved(w.saved[0]["Outfit_ID"])
    assert len(w.saved) == 1


def test_edgy_and_anchor(window):
    w, _ = window
    w.edgy.setChecked(True)
    w.create_outfit(new=True)
    assert w.current[0].edgy
    w.outfit_from(w.wardrobe[0])
    assert w.anchor_id == w.wardrobe[0]["Clothing_ID"]
    w.select_anchor(None)
    assert w.anchor_id is None
