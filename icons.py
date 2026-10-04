"""Pixelart-Icons des Klamotten Kurators, im Code gezeichnet (keine Bilddateien).

Jedes Kleidungs-Icon ist eine Silhouette auf einem 16x16-Raster. Aus der Silhouette entstehen
Umriss, Licht und Schatten automatisch. Gefüllt wird sie mit der Farbe des Kleidungsstücks.
Hochskaliert wird ohne Weichzeichnen, damit die Pixel scharf bleiben.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap

SIZE = 16
OUTLINE = "#B9BDC1"
DIM_FILL, DIM_OUTLINE = "#2A2D2F", "#4A4E52"
ACCENT, BG = "#C9F745", "#111214"

# Silhouetten: Zeilen mit Spannen (von, bis) inklusive, optional "details": Schattenzellen
# (zeile_von, zeile_bis, spalte_von, spalte_bis). Die Form wird automatisch zentriert.
SHAPES = {
    "Top": {   # T-Shirt
        "rows": [[(3, 5), (8, 10)], [(1, 5), (8, 12)], [(0, 13)], [(0, 13)], [(1, 12)]]
                + [[(3, 10)]] * 9,
        "details": [(0, 1, 6, 7)],
    },
    "Bottom": {   # Hose
        "rows": [[(2, 11)]] * 4 + [[(2, 11)]] + [[(2, 5), (8, 11)]] * 9,
        "details": [(0, 0, 2, 11)],
    },
    "Footwear": {   # Stiefel von der Seite
        "rows": [[(2, 6)]] * 7 + [[(2, 7)], [(2, 9)], [(2, 11)], [(1, 12)], [(1, 13)], [(1, 13)]],
        "details": [(12, 12, 1, 13)],
    },
    "Socks": {   # Socke
        "rows": [[(3, 7)]] * 8 + [[(3, 9)], [(3, 11)], [(3, 12)], [(3, 12)]],
        "details": [(0, 1, 3, 7)],
    },
    "Outerwear": {   # Jacke mit Reißverschluss
        "rows": [[(3, 5), (8, 10)], [(2, 5), (8, 11)]] + [[(0, 13)]] * 9 + [[(3, 10)]] * 3,
        "details": [(2, 13, 6, 6), (4, 10, 3, 3), (4, 10, 10, 10)],
    },
    "Headwear": {   # Kappe von der Seite
        "rows": [[(4, 8)], [(3, 9)], [(2, 10)], [(2, 10)], [(2, 10)], [(1, 13)], [(1, 13)]],
        "details": [(1, 4, 6, 6), (5, 6, 1, 13)],
    },
}

# Logo (Kleiderbügel) als Zeichenraster: L = Linie.
LOGO = [
    "......LLL.......",
    ".....L...L......",
    ".....L...L......",
    ".........L......",
    ".........L......",
    "........LL......",
    ".......L..L.....",
    "......L....L....",
    ".....L......L...",
    "....L........L..",
    "...L..........L.",
    "..LLLLLLLLLLLLLL",
    "................",
    "................",
    "................",
    "................",
]


def _mix(color, target, amount):
    c, t = QColor(color), QColor(target)
    return QColor(round(c.red() + (t.red() - c.red()) * amount),
                  round(c.green() + (t.green() - c.green()) * amount),
                  round(c.blue() + (t.blue() - c.blue()) * amount))


def cells(category):
    """Menge der Rasterzellen (zeile, spalte) der zentrierten Silhouette plus Schattenzellen."""
    shape = SHAPES[category]
    filled = {(r, c) for r, spans in enumerate(shape["rows"]) for a, b in spans for c in range(a, b + 1)}
    shaded = {(r, c) for r0, r1, c0, c1 in shape["details"] for r in range(r0, r1 + 1)
              for c in range(c0, c1 + 1) if (r, c) in filled}
    rows = [r for r, _ in filled]
    cols = [c for _, c in filled]
    dr = (SIZE - (max(rows) - min(rows) + 1)) // 2 - min(rows)
    dc = (SIZE - (max(cols) - min(cols) + 1)) // 2 - min(cols)
    move = lambda cs: {(r + dr, c + dc) for r, c in cs}
    return move(filled), move(shaded)


def render(category, fill="#8E9296", dim=False):
    """16x16-Bild des Icons. dim=True: blasse Variante (leerer Slot, gelöschtes Teil)."""
    filled, detail = cells(category)
    if dim:
        body, light, dark, line = (QColor(DIM_FILL),) * 3 + (QColor(DIM_OUTLINE),)
    else:
        body = QColor(fill)
        light, dark, line = _mix(fill, "#FFFFFF", 0.30), _mix(fill, "#000000", 0.28), QColor(OUTLINE)
    image = QImage(SIZE, SIZE, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    for r in range(SIZE):
        for c in range(SIZE):
            if (r, c) in filled:
                if (r, c) in detail or (r + 1, c) not in filled or (r, c + 1) not in filled:
                    color = dark
                elif (r - 1, c) not in filled or (r, c - 1) not in filled:
                    color = light
                else:
                    color = body
                image.setPixelColor(c, r, color)
            elif any((r + dr, c + dc) in filled for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                image.setPixelColor(c, r, line)
    return image


def render_logo(background=False):
    image = QImage(SIZE, SIZE, QImage.Format_ARGB32)
    image.fill(QColor(BG) if background else Qt.transparent)
    for r, row in enumerate(LOGO):
        for c, ch in enumerate(row):
            if ch == "L":
                image.setPixelColor(c, r, QColor(ACCENT))
    return image


def _scaled(image, scale):
    return QPixmap.fromImage(image).scaled(SIZE * scale, SIZE * scale, Qt.KeepAspectRatio, Qt.FastTransformation)


def pixmap(category, fill="#8E9296", scale=4, dim=False):
    return _scaled(render(category, fill, dim), scale)


def logo_pixmap(scale=2, background=False):
    return _scaled(render_logo(background), scale)


def app_icon():
    icon = QIcon()
    for scale in (1, 2, 3, 4, 8, 16):
        icon.addPixmap(logo_pixmap(scale, background=True))
    return icon


if __name__ == "__main__":
    # py icons.py  ->  schreibt assets/klamottenkurator.ico für den .exe-Build
    import sys
    from pathlib import Path
    from PySide6.QtGui import QGuiApplication
    QGuiApplication(sys.argv)
    target = Path(__file__).with_name("assets") / "klamottenkurator.ico"
    target.parent.mkdir(exist_ok=True)
    ok = logo_pixmap(16, background=True).save(str(target), "ICO")
    print(f"{target}: {'ok' if ok else 'failed'}")
    sys.exit(0 if ok else 1)
