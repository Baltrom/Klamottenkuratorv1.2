"""Grafische Oberfläche des Klamotten Kurators (PySide6).

Seiten: Home, My Wardrobe (Teile ansehen, hinzufügen, bearbeiten, löschen),
Outfits (Outfit erstellen, speichern, gespeicherte Outfits ansehen).
Alle Begriffe in der Oberfläche sind Englisch und stammen aus den JSON-Attributen.
Keine Fotos, nur Pixelart-Icons aus icons.py. Start: py gui.py
"""

import sys
import textwrap

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QApplication, QButtonGroup, QDialog, QFrame,
                               QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu,
                               QMessageBox, QPushButton, QScrollArea, QStackedWidget,
                               QToolButton, QVBoxLayout, QWidget)

import icons
import saved_outfits as so
import wardrobe as wd
from outfit_engine import suggest_outfit

BG, PANEL, TEXT, ACCENT, MUTED = "#111214", "#202223", "#F4F4F1", "#C9F745", "#8E9296"
DANGER = "#FF6B6B"

# Farben der Kleidungsstücke, mit ihnen werden die Pixelart-Icons gefüllt.
COLOR_HEX = {"White": "#F4F4F1", "Black": "#0B0B0C", "Grey": "#8A8D91", "Beige": "#D9C7A3",
             "Cream": "#EFE6CC", "Navy": "#1D2B4F", "Brown": "#6B4426", "Blue": "#2F6FD1",
             "Light Blue": "#8EC3EE", "Olive Green": "#6B7A2E", "Burgundy": "#7A1F36"}

STYLE = f"""
QWidget {{ background: {BG}; color: {TEXT}; font-family: "Bahnschrift", "Segoe UI"; font-size: 14px; }}
QLabel {{ background: transparent; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ border: none; background: {BG}; }}
QFrame#card {{ background: {PANEL}; border: 1px solid #2E3032; border-radius: 10px; }}
QScrollBar:vertical {{ background: {BG}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #3A3D40; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: {BG}; }}
QFrame#accentcard {{ background: {PANEL}; border: 1px solid {ACCENT}; border-radius: 10px; }}
QLabel#h1 {{ font-size: 40px; font-weight: bold; }}
QLabel#h2 {{ font-size: 24px; font-weight: bold; }}
QLabel#accent {{ color: {ACCENT}; }}
QLabel#muted {{ color: {MUTED}; font-size: 12px; }}
QLabel#danger {{ color: {DANGER}; }}
QLabel#tag {{ background: {PANEL}; border: 1px solid #3A3D40; border-radius: 6px; padding: 3px 9px;
             font-size: 12px; }}
QLabel#logo {{ font-size: 15px; font-weight: bold; }}
QPushButton {{ background: {PANEL}; border: 1px solid #3A3D40; border-radius: 8px; padding: 8px 16px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton#primary {{ background: {ACCENT}; color: #111214; border: none; font-weight: bold; }}
QPushButton#primary:hover {{ background: #D8FF66; }}
QPushButton#nav {{ background: transparent; border: none; border-radius: 8px; padding: 6px 14px; }}
QPushButton#nav:checked {{ background: {ACCENT}; color: #111214; font-weight: bold; }}
QPushButton#chip {{ border-radius: 14px; padding: 5px 14px; }}
QPushButton#chip:checked {{ background: {ACCENT}; color: #111214; border-color: {ACCENT}; font-weight: bold; }}
QPushButton#menu {{ border: none; background: transparent; padding: 0 6px; font-size: 18px; }}
QPushButton#menu::menu-indicator {{ image: none; width: 0px; }}
QPushButton#big {{ text-align: left; padding: 22px; font-size: 16px; border-radius: 10px; }}
QPushButton#bigaccent {{ text-align: left; padding: 22px; font-size: 16px; border-radius: 10px;
                        border: 1px solid {ACCENT}; }}
QLineEdit {{ background: {PANEL}; border: 1px solid #3A3D40; border-radius: 8px; padding: 7px 10px; }}
QToolButton#tile {{ background: #17191A; border: 1px solid #2E3032; border-radius: 10px; padding: 4px;
                   font-size: 11px; color: {TEXT}; }}
QToolButton#tile:hover {{ border-color: #6A6E73; }}
QToolButton#tile:checked {{ border: 2px solid {ACCENT}; background: #1E2112; }}
QDialog {{ background: {BG}; }}
QMenu {{ background: {PANEL}; border: 1px solid #3A3D40; }}
QMenu::item:selected {{ background: {ACCENT}; color: #111214; }}
"""


def label(text, name=None, wrap=False):
    lab = QLabel(text)
    if name:
        lab.setObjectName(name)
    lab.setWordWrap(wrap)
    return lab


def chip(text, checkable=True):
    b = QPushButton(text)
    b.setObjectName("chip")
    b.setCheckable(checkable)
    b.setCursor(Qt.PointingHandCursor)
    return b


def button(text, name=None):
    b = QPushButton(text)
    if name:
        b.setObjectName(name)
    b.setCursor(Qt.PointingHandCursor)
    return b


def clear(layout):
    """Entfernt alle Einträge (auch verschachtelte Layouts) sofort aus der Anzeige."""
    while layout.count():
        entry = layout.takeAt(0)
        widget, child = entry.widget(), entry.layout()
        if widget:
            widget.setParent(None)
            widget.deleteLater()
        elif child:
            clear(child)
            child.deleteLater()


class Host(QWidget):
    """Inhalt eines Scrollbereichs: wird nie kleiner als seine Wunschgröße, sondern scrollt."""

    def minimumSizeHint(self):
        return self.sizeHint()


def scroll(widget):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(widget)
    return area


def icon_box(subcategory, color_name=None, dim=False, category=None):
    """Pixelart-Icon der Subcategory in der Farbe des Teils, mittig auf dunklem Feld."""
    box = QLabel()
    box.setAlignment(Qt.AlignCenter)
    box.setFixedHeight(112)
    box.setStyleSheet("background: #17191A; border-radius: 6px; border: 1px solid #2E3032;")
    box.setPixmap(icons.pixmap(subcategory, COLOR_HEX.get(color_name, "#8E9296"), scale=3,
                               dim=dim, category=category))
    return box


def item_tile(text, pixmap):
    """Auswahlkachel (Icon und Name) für das Startteil."""
    tile = QToolButton()
    tile.setObjectName("tile")
    tile.setCheckable(True)
    tile.setCursor(Qt.PointingHandCursor)
    tile.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    tile.setIcon(QIcon(pixmap))
    tile.setIconSize(QSize(64, 64))
    tile.setText("\n".join(textwrap.wrap(text, 16)[:2]))
    tile.setFixedSize(126, 118)
    return tile


def item_meta(item):
    return f"{item['Subcategory']} · {item['Color']}".upper()


# --- Dialog: Teil hinzufügen / bearbeiten ---------------------------------------------

class ItemDialog(QDialog):
    """Auswahl per Buttons: Category → Subcategory → Color → Occasion → Season."""

    def __init__(self, parent, item=None):
        super().__init__(parent)
        self.setWindowTitle("Edit item" if item else "Add item")
        self.setMinimumWidth(620)
        self.cat = self.sub = self.color = None
        self.occasions, self.seasons = set(), set()

        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.addWidget(label("Edit item" if item else "Add item", "h2"))

        self.cat_row = self._row(lay, "Category")
        self.sub_row = self._row(lay, "Subcategory")
        self.color_row = self._row(lay, "Color")
        self.occ_row = self._row(lay, "Occasion (one or more)")
        self.season_row = self._row(lay, "Season (one or more)")

        self.cat_group = self._exclusive(self.cat_row, wd.CATEGORIES, self._pick_category)
        self.color_group = self._exclusive(self.color_row, wd.COLORS, lambda v: setattr(self, "color", v))
        self.sub_group = None
        self._multi(self.occ_row, wd.OCCASIONS, self.occasions)
        self._multi(self.season_row, wd.SEASONS, self.seasons)

        lay.addWidget(label("Name (optional)", "muted"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Default: <Color> <Subcategory>")
        lay.addWidget(self.name_edit)

        self.error = label("", "danger")
        lay.addWidget(self.error)
        row = QHBoxLayout()
        row.addStretch()
        cancel = button("Cancel")
        cancel.clicked.connect(self.reject)
        ok = button("Save", "primary")
        ok.clicked.connect(self._accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        lay.addLayout(row)

        if item:
            self._prefill(item)

    def _row(self, parent_layout, title):
        parent_layout.addWidget(label(title, "muted"))
        row = QHBoxLayout()
        row.setSpacing(6)
        wrapper = QWidget()
        wrapper.setLayout(row)
        parent_layout.addWidget(wrapper)
        return row

    def _exclusive(self, row, values, on_pick):
        group = QButtonGroup(self)
        group.setExclusive(True)
        for v in values:
            b = chip(v)
            b.clicked.connect(lambda _=False, v=v: on_pick(v))
            group.addButton(b)
            row.addWidget(b)
        row.addStretch()
        return group

    def _multi(self, row, values, target):
        for v in values:
            b = chip(v)
            b.toggled.connect(lambda on, v=v: target.add(v) if on else target.discard(v))
            row.addWidget(b)
        row.addStretch()

    def _pick_category(self, category):
        self.cat = category
        self.sub = None
        clear(self.sub_row)
        self.sub_group = self._exclusive(self.sub_row, wd.SUBCATEGORIES[category],
                                         lambda v: setattr(self, "sub", v))

    def _prefill(self, item):
        self._check(self.cat_group, item["Category"])
        self._pick_category(item["Category"])
        self._check(self.sub_group, item["Subcategory"])
        self.sub = item["Subcategory"]
        self._check(self.color_group, item["Color"])
        self.color = item["Color"]
        for row, values in ((self.occ_row, item["Occasion"]), (self.season_row, item["Season"])):
            for i in range(row.count()):
                b = row.itemAt(i).widget()
                if b and b.text() in values:
                    b.setChecked(True)
        self.name_edit.setText(item["Name"])

    @staticmethod
    def _check(group, text):
        for b in group.buttons():
            if b.text() == text:
                b.setChecked(True)

    def _accept(self):
        if not (self.cat and self.sub and self.color and self.occasions and self.seasons):
            self.error.setText("Choose a category, subcategory, color, at least one occasion and one season.")
            return
        self.accept()

    def values(self):
        return dict(category=self.cat, subcategory=self.sub, color=self.color,
                    occasions=[o for o in wd.OCCASIONS if o in self.occasions],
                    seasons=[s for s in wd.SEASONS if s in self.seasons],
                    name=self.name_edit.text().strip() or f"{self.color} {self.sub}")


# --- Karten ------------------------------------------------------------------------------

class ItemCard(QFrame):
    def __init__(self, item, window):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(label(item["Clothing_ID"], "muted"))
        top.addStretch()
        menu_btn = button("⋮", "menu")
        menu = QMenu(menu_btn)
        menu.addAction("Edit", lambda: window.edit_item(item))
        menu.addAction("Build outfit from this item", lambda: window.outfit_from(item))
        menu.addAction("Delete", lambda: window.delete_item(item))
        menu_btn.setMenu(menu)
        top.addWidget(menu_btn)
        lay.addLayout(top)
        lay.addWidget(icon_box(item["Subcategory"], item["Color"], category=item["Category"]))
        lay.addWidget(label(item["Name"], wrap=True))
        lay.addWidget(label(item_meta(item), "muted"))
        lay.addWidget(label(f"{' / '.join(item['Occasion'])} · {', '.join(item['Season'])}", "muted", wrap=True))
        lay.addStretch()


def slot_card(slot, item):
    card = QFrame()
    card.setObjectName("card")
    lay = QVBoxLayout(card)
    lay.addWidget(label(slot.upper(), "muted"))
    if item is None:
        lay.addWidget(icon_box(None, dim=True, category=slot))
        lay.addWidget(label("No suitable item", "muted", wrap=True))
    elif item.get("deleted"):
        lay.addWidget(icon_box(None, dim=True, category=slot))
        lay.addWidget(label(f"{item['Name']} ({item['Clothing_ID']})", "danger", wrap=True))
    else:
        lay.addWidget(icon_box(item["Subcategory"], item["Color"], category=item["Category"]))
        lay.addWidget(label(item["Name"], wrap=True))
        lay.addWidget(label(item_meta(item), "muted"))
    lay.addStretch()
    return card


def tag_row(*texts):
    row = QHBoxLayout()
    for t in texts:
        row.addWidget(label(t.upper(), "tag"))
    row.addStretch()
    return row


# --- Hauptfenster --------------------------------------------------------------------------

class MainWindow(QWidget):
    COLUMNS = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Klamotten Kurator")
        self.resize(1180, 780)
        self.wardrobe = wd.load_wardrobe()
        self.saved = so.load_saved()
        self.filter = "All"
        self.seen, self.current = [], None
        self.anchor_id, self.anchor_filter = None, "All"

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.addLayout(self._header())
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_home())
        self.pages.addWidget(self._build_wardrobe())
        self.pages.addWidget(self._build_outfits())
        root.addWidget(self.pages, 1)
        self.refresh_all()
        self.go(0)

    # Aufbau ----------------------------------------------------------------------------

    def _header(self):
        row = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(icons.logo_pixmap(2))
        row.addWidget(logo)
        row.addWidget(label("KLAMOTTEN\nKURATOR", "logo"))
        row.addSpacing(30)
        self.nav = []
        group = QButtonGroup(self)
        for i, text in enumerate(("Home", "My Wardrobe", "Outfits")):
            b = button(text, "nav")
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, i=i: self.go(i))
            group.addButton(b)
            row.addWidget(b)
            self.nav.append(b)
        row.addStretch()
        return row

    def go(self, index):
        self.pages.setCurrentIndex(index)
        self.nav[index].setChecked(True)

    def _build_home(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 40, 0, 0)
        lay.addWidget(label("Your wardrobe.", "h1"))
        lay.addWidget(label("Newly combined.", "h1 accent"))
        lay.itemAt(1).widget().setStyleSheet(f"color: {ACCENT}; font-size: 40px; font-weight: bold;")
        lay.addWidget(label("Discover new outfits from the clothes you already own.", "muted"))
        lay.addSpacing(20)
        self.stats = label("", "h2")
        lay.addWidget(self.stats)
        lay.addSpacing(20)
        cards = QHBoxLayout()
        self.wardrobe_btn = button("", "big")
        self.wardrobe_btn.clicked.connect(lambda: self.go(1))
        self.outfit_btn = button("Find Outfit\nCombine now  →", "bigaccent")
        self.outfit_btn.clicked.connect(lambda: self.go(2))
        cards.addWidget(self.wardrobe_btn)
        cards.addWidget(self.outfit_btn)
        lay.addLayout(cards)
        add = button("+  Add item", "primary")
        add.setMinimumHeight(44)
        add.clicked.connect(self.add_item)
        lay.addWidget(add)
        lay.addStretch()
        return page

    def _build_wardrobe(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        top = QHBoxLayout()
        top.addWidget(label("My Wardrobe", "h2"))
        top.addStretch()
        add = button("+  Add item", "primary")
        add.clicked.connect(self.add_item)
        top.addWidget(add)
        lay.addLayout(top)

        chips = QHBoxLayout()
        self.filter_group = QButtonGroup(self)
        for name in ["All"] + wd.CATEGORIES:
            b = chip(name)
            b.setChecked(name == "All")
            b.clicked.connect(lambda _=False, n=name: self.set_filter(n))
            self.filter_group.addButton(b)
            chips.addWidget(b)
        chips.addStretch()
        lay.addLayout(chips)

        self.grid_host = Host()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setSpacing(12)
        for c in range(self.COLUMNS):
            self.grid.setColumnStretch(c, 1)
        lay.addWidget(scroll(self.grid_host), 1)
        return page

    def _build_outfits(self):
        host = Host()
        lay = QVBoxLayout(host)
        lay.addWidget(label("Find Outfit", "h2"))

        form = QFrame()
        form.setObjectName("card")
        fl = QVBoxLayout(form)
        anchor_head = QHBoxLayout()
        anchor_head.addWidget(label("Starting item", "muted"))
        self.anchor_label = label("", "accent")
        anchor_head.addWidget(self.anchor_label)
        anchor_head.addStretch()
        fl.addLayout(anchor_head)
        anchor_chips = QHBoxLayout()
        group = QButtonGroup(self)
        for name in ["All"] + wd.CATEGORIES:
            b = chip(name)
            b.setChecked(name == "All")
            b.clicked.connect(lambda _=False, n=name: self.set_anchor_filter(n))
            group.addButton(b)
            anchor_chips.addWidget(b)
        anchor_chips.addStretch()
        self.anchor_chips = group
        fl.addLayout(anchor_chips)
        tiles_host = Host()
        self.tiles = QGridLayout(tiles_host)
        self.tiles.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.tiles.setSpacing(8)
        self.tiles_area = scroll(tiles_host)
        self.tiles_area.setFixedHeight(262)
        fl.addWidget(self.tiles_area)
        fl.addWidget(label("Season", "muted"))
        self.season_group, self.season_row = self._choice(fl, wd.SEASONS, "Autumn")
        fl.addWidget(label("Occasion", "muted"))
        self.occasion_group, self.occasion_row = self._choice(fl, wd.OCCASIONS, "Casual")
        edgy_row = QHBoxLayout()
        self.edgy = chip("Edgy (invert: least fitting outfit)")
        edgy_row.addWidget(self.edgy)
        edgy_row.addStretch()
        fl.addLayout(edgy_row)
        go = button("Create outfit", "primary")
        go.setMinimumHeight(40)
        go.clicked.connect(lambda: self.create_outfit(new=True))
        fl.addWidget(go)
        lay.addWidget(form)

        self.result_box = QVBoxLayout()
        lay.addLayout(self.result_box)
        lay.addSpacing(10)
        lay.addWidget(label("Saved outfits", "h2"))
        self.saved_box = QVBoxLayout()
        lay.addLayout(self.saved_box)
        lay.addStretch()
        return scroll(host)

    def _choice(self, parent_layout, values, default):
        row = QHBoxLayout()
        group = QButtonGroup(self)
        group.setExclusive(True)
        for v in values:
            b = chip(v)
            b.setChecked(v == default)
            group.addButton(b)
            row.addWidget(b)
        row.addStretch()
        parent_layout.addLayout(row)
        return group, row

    # Aktualisieren ---------------------------------------------------------------------

    def refresh_all(self):
        n = len(self.wardrobe)
        self.stats.setText(f"{n} ITEMS   ·   {len(wd.OCCASIONS)} OCCASIONS   ·   {len(wd.SEASONS)} SEASONS")
        self.wardrobe_btn.setText(f"My Wardrobe\n{n} items  →")
        self.refresh_grid()
        self.refresh_anchor_box()
        self.refresh_saved()

    def set_filter(self, name):
        self.filter = name
        self.refresh_grid()

    def refresh_grid(self):
        clear(self.grid)
        items = [i for i in self.wardrobe if self.filter in ("All", i["Category"])]
        if not items:
            self.grid.addWidget(label("No items here yet. Use “Add item”.", "muted"), 0, 0)
        for n, item in enumerate(items):
            self.grid.addWidget(ItemCard(item, self), n // self.COLUMNS, n % self.COLUMNS)
        rows = (len(items) + self.COLUMNS - 1) // self.COLUMNS
        for r in range(rows + 1):
            self.grid.setRowStretch(r, 0)
        self.grid.setRowStretch(rows, 1)  # überschüssiger Platz nach unten, Karten bleiben kompakt

    TILE_COLUMNS = 8

    def refresh_anchor_box(self, select_id=None):
        """Baut die Kacheln für das Startteil neu auf (gefiltert nach Category)."""
        if select_id is not None:
            self.anchor_id = select_id
        if not any(i["Clothing_ID"] == self.anchor_id for i in self.wardrobe):
            self.anchor_id = None
        clear(self.tiles)
        self.selected_tile = None
        self.tile_group = QButtonGroup(self)
        none_tile = item_tile("No starting item", icons.logo_pixmap(4))
        none_tile.setChecked(self.anchor_id is None)
        none_tile.clicked.connect(lambda: self.select_anchor(None))
        self.tile_group.addButton(none_tile)
        self.tiles.addWidget(none_tile, 0, 0)
        items = sorted((i for i in self.wardrobe if self.anchor_filter in ("All", i["Category"])),
                       key=lambda i: (wd.CATEGORIES.index(i["Category"]), i["Name"]))
        for n, item in enumerate(items, start=1):
            tile = item_tile(item["Name"], icons.pixmap(item["Subcategory"], COLOR_HEX.get(item["Color"], MUTED),
                                                        scale=2, category=item["Category"]))
            tile.setToolTip(f"{item['Name']} ({item['Clothing_ID']})\n{item_meta(item)}")
            tile.setChecked(item["Clothing_ID"] == self.anchor_id)
            if tile.isChecked():
                self.selected_tile = tile
            tile.clicked.connect(lambda _=False, cid=item["Clothing_ID"]: self.select_anchor(cid))
            self.tile_group.addButton(tile)
            self.tiles.addWidget(tile, n // self.TILE_COLUMNS, n % self.TILE_COLUMNS)
        self._update_anchor_label()

    def set_anchor_filter(self, name):
        self.anchor_filter = name
        self.refresh_anchor_box()

    def select_anchor(self, clothing_id):
        self.anchor_id = clothing_id
        self._update_anchor_label()

    def _update_anchor_label(self):
        item = next((i for i in self.wardrobe if i["Clothing_ID"] == self.anchor_id), None)
        self.anchor_label.setText(f"·  {item['Name']} ({item['Clothing_ID']})" if item else "·  none")

    def refresh_saved(self):
        clear(self.saved_box)
        if not self.saved:
            self.saved_box.addWidget(label("Nothing saved yet.", "muted"))
        for record in reversed(self.saved):
            self.saved_box.addWidget(self._saved_card(record))

    def _saved_card(self, record):
        slots, has_deleted = so.resolve_outfit(record, self.wardrobe)
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        top = QHBoxLayout()
        tags = [record["Occasion"], record["Season"]] + (["Edgy"] if record["Edgy"] else [])
        top.addLayout(tag_row(*tags))
        top.addWidget(label(f"{record['Outfit_ID']} · saved {record['Saved']}", "muted"))
        delete = button("Delete")
        delete.clicked.connect(lambda: self.delete_saved(record["Outfit_ID"]))
        top.addWidget(delete)
        lay.addLayout(top)
        for slot, item in slots.items():
            if item is None:
                continue
            deleted = item.get("deleted")
            text = f"{slot:<10} {item['Name']}" + (f" ({item['Clothing_ID']})" if deleted else "")
            lay.addWidget(label(text, "danger" if deleted else None))
        if has_deleted:
            lay.addWidget(label("This outfit contains a deleted item.", "danger"))
        return card

    # Aktionen: Kleiderschrank ----------------------------------------------------------

    def _error(self, text):
        QMessageBox.warning(self, "Klamotten Kurator", text)

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec() == QDialog.Accepted:
            v = dialog.values()
            try:
                wd.add_item(self.wardrobe, v["category"], v["subcategory"], v["color"],
                            v["occasions"], v["seasons"], name=v["name"])
            except (wd.ClothingDataError, OSError) as e:
                self._error(str(e))
            self.refresh_all()

    def edit_item(self, item):
        dialog = ItemDialog(self, item)
        if dialog.exec() == QDialog.Accepted:
            try:
                wd.update_item(self.wardrobe, item["Clothing_ID"], **dialog.values())
            except (wd.ClothingDataError, ValueError, OSError) as e:
                self._error(str(e))
            self.refresh_all()

    def delete_item(self, item):
        used = sum(1 for r in self.saved if item["Clothing_ID"] in r["Items"].values())
        note = f"\n\n{used} saved outfit(s) use it and will show it as “(deleted)”." if used else ""
        answer = QMessageBox.question(self, "Delete item", f"Delete “{item['Name']}” ({item['Clothing_ID']})?{note}")
        if answer == QMessageBox.Yes:
            try:
                wd.delete_item(self.wardrobe, item["Clothing_ID"])
            except (ValueError, OSError) as e:
                self._error(str(e))
            self.refresh_all()

    def outfit_from(self, item):
        self.anchor_filter = item["Category"]
        for b in self.anchor_chips.buttons():
            b.setChecked(b.text() == item["Category"])
        self.refresh_anchor_box(select_id=item["Clothing_ID"])
        self.go(2)
        if self.selected_tile:
            self.tiles_area.ensureWidgetVisible(self.selected_tile)

    # Aktionen: Outfits -----------------------------------------------------------------

    def _selected(self, group):
        return next(b.text() for b in group.buttons() if b.isChecked())

    def create_outfit(self, new):
        if new:
            self.seen = []
        season, occasion = self._selected(self.season_group), self._selected(self.occasion_group)
        anchor = self.anchor_id
        clear(self.result_box)
        try:
            outfit = suggest_outfit(self.wardrobe, anchor, season, occasion,
                                    edgy=self.edgy.isChecked(), exclude=self.seen)
        except ValueError as e:
            self.current = None
            self.result_box.addWidget(label(str(e), "danger"))
            return
        self.seen.append(outfit.key)
        self.current = (outfit, season, occasion, anchor)
        self._show_outfit(outfit, season, occasion)

    def _show_outfit(self, outfit, season, occasion):
        box = self.result_box
        box.addWidget(label("Your Outfit", "h2"))
        box.addLayout(tag_row(occasion, season, *(["Edgy"] if outfit.edgy else []),
                              *(["Suit"] if outfit.suit else [])))
        cards = QHBoxLayout()
        for slot, item in outfit.slots.items():
            cards.addWidget(slot_card(slot, item))
        box.addLayout(cards)
        name = "Edginess" if outfit.edgy else "Compatibility"
        box.addWidget(label(f"{name} {outfit.score:.0f}/100   (season {outfit.season:.2f}, "
                            f"occasion {outfit.occasion:.2f}, color {outfit.color:.2f})", "muted"))
        self.status = label("", "accent")
        buttons = QHBoxLayout()
        save = button("Save outfit", "primary")
        save.clicked.connect(self.save_current)
        other = button("Another combination")
        other.clicked.connect(lambda: self.create_outfit(new=False))
        buttons.addWidget(save)
        buttons.addWidget(other)
        box.addLayout(buttons)
        box.addWidget(self.status)

    def save_current(self):
        if not self.current:
            return
        outfit, season, occasion, anchor = self.current
        try:
            record = so.save_outfit(self.saved, outfit, season, occasion, anchor)
        except ValueError as e:
            self.status.setText(str(e))
            return
        except OSError as e:
            self._error(str(e))
            return
        self.status.setText(f"Saved as {record['Outfit_ID']}.")
        self.refresh_saved()

    def delete_saved(self, outfit_id):
        try:
            so.delete_saved(self.saved, outfit_id)
        except (ValueError, OSError) as e:
            self._error(str(e))
        self.refresh_saved()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Bahnschrift", 10))
    app.setStyleSheet(STYLE)
    app.setWindowIcon(icons.app_icon())
    try:
        window = MainWindow()
    except (wd.ClothingDataError, OSError) as e:
        QMessageBox.critical(None, "Klamotten Kurator", f"The data could not be loaded:\n\n{e}")
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
