"""Pixelart-Icons des Klamotten Kurators, im Code gezeichnet (keine Bilddateien).

Ein Icon pro Subcategory, 32x32 Pixel, ohne Umriss. Nur sehr dunkle Farben, die sich kaum von der
dunklen Kachel abheben (z. B. Black, Burgundy), bekommen einen hellen 1-Pixel-Umriss. Jedes Icon ist ein Zeichenraster:
Flächen ('#', '+', '%') werden automatisch schattiert (Licht von links oben, jede Fläche
wirkt leicht gepolstert), '#' bekommt zusätzlich die Stoffstruktur des Icons (Denim, Strick, ...).
Gefüllt wird mit der Farbe des Kleidungsstücks, Details wie Kordeln, Metall und Sohlen haben
feste Farben. Hochskaliert wird ohne Weichzeichnen, damit die Pixel scharf bleiben.

Legende der Raster:
  .  leer               #  Hauptfläche (mit Stoffstruktur)   +  zweite Fläche   %  dritte Fläche
  r  Rippenstrick       x  Naht                               1-5  feste Stufe (1 dunkel ... 5 Glanz)
  s/S Kordel/Schatten   m/n Metall hell/dunkel                g  Ziernaht (gold)
  w/W Sohle weiß/grau   k/K Gummi dunkel/hell                 b  Ledersohle   L  Lime-Akzent
  f  Fell (Parka)
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap

SIZE = 32
ACCENT, BG = "#C9F745", "#111214"
TILE = "#17191A"           # Hintergrund der Icon-Felder in der GUI
MIN_CONTRAST = 2.0         # darunter bekommt das Icon einen Umriss
PANELS = "#+%"
FIXED = {"s": "#F1EEE6", "S": "#C4BFB2", "m": "#DADEE2", "n": "#868C93", "g": "#E2AC4E",
         "w": "#F2F1EC", "W": "#C9C7BE", "k": "#2E3034", "K": "#4C4F55", "b": "#6E4A2E",
         "L": ACCENT, "f": "#E3D5B8"}
DIM_BASE = "#3A3D41"

# Icon-Definitionen. "half": linke Hälfte (16 breit), wird gespiegelt. "rows": volle Zeilen.
# "stamps": (x, y, Zeilen) nach dem Spiegeln, Leerzeichen = nichts ändern.
ICONS = {
    # --- Top -----------------------------------------------------------------------------
    "T-Shirt": {"half": [
        ".......####r1111",
        ".....#######r111",
        "...##########rrr",
        "..###x##########",
        ".####x##########",
        "#####x##########",
        "#####x##########",
        "xxxxxx##########",
        "#####x##########",
        "...##x##########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....xxxxxxxxxxx",
        ".....###########",
        "......##########",
    ]},
    "Polo Shirt": {"half": [
        ".......####+++++",
        ".....#####+++111",
        "...#######++++11",
        "..###x####+++++%",
        ".####x#####+++%%",
        "#####x######++%s",
        "#####x########%%",
        "rrrrrx########%%",
        "#####x########%s",
        "...##x########%%",
        ".....#########xx",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....###########",
        ".....rrrrrrrrrrr",
        ".....###########",
        "......##########",
    ]},
    "Tank Top": {"half": [
        "......###.......",
        "......###.......",
        "......###.......",
        "......####......",
        "......####r.....",
        ".....######r....",
        "....########rr..",
        "....##########rr",
        "....############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...#############",
        "...xxxxxxxxxxxxx",
        "...#############",
        "....############",
    ], "texture": "rib", "round": False},
    "Long Sleeve Top": {"half": [
        ".......####r1111",
        ".....#######r111",
        "...##########rrr",
        "..###x##########",
        ".####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "rrrrrx##########",
        "rrrrrx##########",
        ".....###########",
        ".....xxxxxxxxxxx",
        ".....###########",
        "......##########",
    ], "texture": "stripes"},
    "Shirt": {"half": [
        ".......####+++++",
        ".....#####+++111",
        "...#######++++11",
        "..###x####+++++%",
        ".####x#####++++%",
        "#####x######+++s",
        "#####x########+%",
        "#####x#########%",
        "#####x#########%",
        "#####x#########s",
        "#####x#########%",
        "#####x#########%",
        "#####x#########%",
        "#####x#########s",
        "#####x#########%",
        "#####x#########%",
        "#####x#########%",
        "+++++x#########s",
        "++s++x#########%",
        ".....##########%",
        ".....##########%",
        "......#########%",
        "........#######%",
    ], "stamps": [(8, 8, ["xxxxx", "+++++", "+++++", "+++++", "++++ "])]},
    "Hoodie": {"half": [
        "..........######",
        "........########",
        ".......####41111",
        "......####411111",
        "......####411111",
        "....######411111",
        "..########411111",
        ".##########41s11",
        "#####x######4s11",
        "#####x#######s#1",
        "#####x#######s##",
        "#####x#######s##",
        "#####x#######m##",
        "#####x#######n##",
        "#####x##########",
        "#####x####++++++",
        "#####x###1++++++",
        "#####x###1++++++",
        "rrrrrx##1+++++++",
        "rrrrrx##1+++++++",
        ".....###########",
        ".....rrrrrrrrrrr",
        ".....rrrrrrrrrrr",
        "......rrrrrrrrrr",
    ], "texture": "fleece"},
    "Sweater": {"half": [
        ".......####rrrrr",
        ".....######r1111",
        "...#########rrrr",
        "..###x##########",
        ".####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x#+#+#+#+#+",
        "#####x+#+#+#+#+#",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "#####x##########",
        "rrrrrx##########",
        "rrrrrx##########",
        ".....###########",
        ".....rrrrrrrrrrr",
        ".....rrrrrrrrrrr",
        "......rrrrrrrrrr",
    ], "texture": "knit"},
    # --- Bottom --------------------------------------------------------------------------
    "Jeans": {"half": [
        "...+x+++++x+++++",
        "...+x+++++x++++m",
        "...#############",
        "...###g######g##",
        "...##g#######g##",
        "...#g########g##",
        "...##########g##",
        "...###########g#",
        "...#############",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...+++++++++++..",
        "...+++++++++++..",
    ], "texture": "denim"},
    "Trousers": {"half": [
        "...kkkkkkkkkkkmm",
        "...kkkkkkkkkkkmm",
        "...#############",
        "...###x#######x#",
        "...##x########x#",
        "...#x#########x#",
        "...###########x#",
        "...#############",
        "...###########..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...#####4#####..",
        "...xxxxxxxxxxx..",
    ]},
    "Chinos": {"half": [
        "...+x+++++x+++++",
        "...+x+++++x++++m",
        "...#############",
        "...####x######x#",
        "...###x#######x#",
        "...##x########x#",
        "...#x#########x#",
        "...#############",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "....##########..",
        "....##########..",
        "....##########..",
        "....##########..",
        "....##########..",
        "....##########..",
        "....++++++++++..",
        "....++++++++++..",
    ]},
    "Cargo Pants": {"half": [
        "...+x+++++x+++++",
        "...+x+++++x++++m",
        "...#############",
        "...###########x#",
        "...###########x#",
        "...###########x#",
        "...#############",
        "...###########..",
        "...###########..",
        "...###########..",
        "..xxxxxxx#####..",
        "..+++++++#####..",
        "..+++m+++#####..",
        "..%%%%%%%#####..",
        "..%%%%%%%#####..",
        "..%%%%%%%#####..",
        "..%%%%%%%#####..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...rrrrrrrrrrr..",
        "...rrrrrrrrrrr..",
    ], "texture": "ripstop"},
    "Sweatpants": {"half": [
        "...rrrrrrrrrrrrr",
        "...rrrrrrrrrrrrr",
        "...##########s##",
        "...##x#######s##",
        "...#x########S##",
        "...##########S##",
        "...#############",
        "...#############",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "...###########..",
        "....##########..",
        "....##########..",
        "....##########..",
        "....##########..",
        ".....#########..",
        ".....rrrrrrrrr..",
        ".....rrrrrrrrr..",
    ], "texture": "fleece"},
    "Shorts": {"half": [
        "...+x+++++x+++++",
        "...+x+++++x++++m",
        "...#############",
        "...####x######x#",
        "...###x#######x#",
        "...##x########x#",
        "...#############",
        "...###########..",
        "..############..",
        "..############..",
        "..############..",
        "..############..",
        "..++++++++++++..",
        "..++++++++++++..",
    ]},
    "Athletic Shorts": {"half": [
        "..rrrrrrrrrrrrrr",
        "..rrrrrrrrrrrrrr",
        "..s##########s##",
        "..s##########s##",
        "..s##########S##",
        "..s#############",
        "..s###########..",
        "..s###########..",
        "..s###########..",
        "..s###########..",
        "..s###########..",
        "...s##########..",
        "....#########...",
    ], "texture": "mesh"},
    # --- Footwear (Seitenansicht, Spitze nach rechts) ---------------------------------------
    "Sneakers": {"rows": [
        "..........+++",
        ".........+++++",
        "...###...+++++",
        "..#####11+++++",
        ".######11+++++#",
        ".######11++++####",
        ".##################",
        ".#####################",
        ".########################",
        ".##########################",
        ".###########################",
        ".############################",
        ".############################",
        ".############################",
        ".wwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        ".wwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        ".WWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "..KKKKKKKKKKKKKKKKKKKKKKKKKKK",
    ], "stamps": [(1, 4, ["+"]), (1, 5, ["+"]),
                  (13, 5, ["ssn"]), (15, 6, ["ssn"]), (17, 7, ["ssn"]), (19, 8, ["ssn"]),
                  (24, 10, ["wwww"]), (23, 11, ["wwwww"]), (22, 12, ["wwwwww"]), (22, 13, ["wwwwww"]),
                  (4, 11, ["LL"]), (6, 12, ["LLLLLL"]), (12, 11, ["LLLL"]), (16, 10, ["LL"]),
                  (3, 4, ["5"]), (2, 5, ["5"])]},
    "Running Shoes": {"rows": [
        "..........++",
        "....##...++++",
        "...####11++++",
        "..#####11+++++#",
        ".######11++++####",
        ".##################",
        ".######################",
        ".#########################",
        ".###########################",
        ".############################",
        "..############################",
        ".wwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        ".wwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        ".wwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "..WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "...KKKKKKKKKKKKKKKKKKKKKKKK",
    ], "texture": "mesh",
        "stamps": [(13, 4, ["ssn"]), (15, 5, ["ssn"]), (17, 6, ["ssn"]), (19, 7, ["ssn"]),
                   (1, 5, ["%%%"]), (1, 6, ["%%%%"]), (1, 7, ["%%%%%"]), (1, 8, ["%%%%"]), (1, 9, ["%%%"]),
                   (23, 8, ["%%%%"]), (22, 9, ["%%%%%%"]), (22, 10, ["%%%%%%%"]),
                   (3, 12, ["LLL    LLL    LLL    LLL"]), (6, 13, ["L      L      L      L"]),
                   (7, 8, ["LLLL"]), (11, 7, ["LLL"]), (14, 6, ["L"])]},
    "Boots": {"rows": [
        "..++++++++++",
        "..##########",
        "..##########",
        "..##########",
        "..##########",
        "..##########",
        "..##########",
        "..##########",
        "..##########",
        "..#############",
        "..################",
        "..####################",
        ".#######################",
        ".#########################",
        ".##########################",
        ".bbbbbbbbbbbbbbbbbbbbbbbbbb",
        ".kkkkkkkkkkkkkkkkkkkkkkkkkk",
        ".kkk..kkk..kkk..kkk..kkkkk",
    ], "stamps": [(8, 1, ["nss"]), (8, 3, ["nss"]), (8, 5, ["nss"]), (8, 7, ["nss"]), (10, 9, ["nss"]),
                  (11, 0, ["+"]), (3, 2, ["5"]), (3, 3, ["5"]), (3, 4, ["5"]),
                  (20, 12, ["55"]), (22, 13, ["5"]),
                  (1, 15, [" g g g g g g g g g g g g g"]),
                  (5, 9, ["x"]), (5, 10, ["x"]), (5, 11, ["x"]), (5, 12, ["x"]), (5, 13, ["x"]), (5, 14, ["x"])]},
    "Loafers": {"rows": [
        "...####",
        "..#####1111111",
        ".######11111111###",
        ".#######1111111######",
        ".########+++++++#######",
        ".########++111++#########",
        ".########+++++++###########",
        ".##########################",
        ".###########################",
        ".############################",
        ".############################",
        ".bbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "..kkkkkk",
    ], "stamps": [(17, 7, ["xxxxxxxx"]), (25, 8, ["55"]), (3, 1, ["5"]), (2, 2, ["5"]),
                  (1, 11, [" g g g g g g g g g g g g g g"])]},
    # --- Socks (Seitenansicht) ----------------------------------------------------------
    "Ankle Socks": {"rows": [
        "..+rrrrrrrrrrr",
        "..+rrrrrrrrrrr",
        "...###########",
        "...############",
        "..+++++##############",
        "..++++++###############",
        "..++++++##############++++",
        "..++++++###############++++",
        "...+++++###############++++",
        "....##################++",
    ]},
    "Crew Socks": {"rows": [
        "....rrrrrrrrrrr",
        "....rrrrrrrrrrr",
        "....rrrrrrrrrrr",
        "....###########",
        "....11111111111",
        "....###########",
        "....11111111111",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....############",
        "....##############",
        "...++++#############",
        "...+++++###############",
        "...+++++################",
        "...+++++##############++++",
        "...+++++###############++++",
        "....++++###############++++",
        ".....##################++",
    ]},
    "Wool Socks": {"rows": [
        "...rrrrrrrrrrrrr",
        "...rrrrrrrrrrrrr",
        "...rrrrrrrrrrrrr",
        "...rrrrrrrrrrrrr",
        "....###########",
        "....#s#s#s#s#s#",
        "....s#s#s#s#s#s",
        "....#s#s#s#s#s#",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....###########",
        "....############",
        "....##############",
        "...++++#############",
        "...+++++###############",
        "...+++++################",
        "...+++++##############++++",
        "...+++++###############++++",
        "....++++###############++++",
        ".....##################++",
    ], "texture": "knit"},
    # --- Outerwear -----------------------------------------------------------------------
    "Bomber Jacket": {"half": [
        "........###rrrrr",
        "......#####rrrrn",
        "....########rr#n",
        "..###x#########n",
        ".####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x###x#####n",
        "#####x####x####n",
        "#####x#####x###n",
        "#####x#########n",
        "#####x#########n",
        "rrrrrx#########n",
        "rrrrrx#########n",
        ".....rrrrrrrrrrn",
        ".....rrrrrrrrrrn",
        "......rrrrrrrrrn",
    ], "texture": "gloss", "stamps": [(15, 3, ["mm"]), (16, 3, ["m"]), (1, 7, ["mmm"])]},
    "Denim Jacket": {"half": [
        ".......####+++++",
        ".....#####+++111",
        "...#######++++11",
        "..###x####+++++%",
        ".####x#####++++%",
        "#####x######+++g",
        "#####xggggg###+%",
        "#####x+++++####%",
        "#####x#+g+#####%",
        "#####x#########g",
        "#####x#########%",
        "#####x#########%",
        "#####x#########%",
        "#####x#########g",
        "#####x#########%",
        "#####x#########%",
        "#####xggggggggg%",
        "+++++x+++++++++%",
        "++g++x++++g++++g",
        ".....++++++++++%",
    ], "texture": "denim"},
    "Jacket": {"half": [
        ".......####+++++",
        ".....######++++n",
        "...#########+++n",
        "..###x#########n",
        ".####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#xxxxx###n",
        "#####x#+++++###n",
        "#####x#%%%%%###n",
        "#####x#%%%%%###n",
        "#####x#########n",
        "+++++x#########n",
        "+++++x#########n",
        ".....##########n",
        ".....xxxxxxxxxxn",
        ".....##########n",
    ], "stamps": [(15, 3, ["mm"])]},
    "Rain Jacket": {"half": [
        "..........######",
        "........########",
        ".......####41111",
        "......####411111",
        "......####411111",
        "....######411111",
        "..########411111",
        ".##########4111+",
        "#####x######m#++",
        "#####x########++",
        "#####x########m+",
        "#####x########++",
        "#####x########++",
        "#####x########++",
        "#####x#xxxx###m+",
        "#####x#++++###++",
        "#####x#%%%%###++",
        "#####x#%%%%###++",
        "+++++x########m+",
        "+++++x########++",
        ".....#########++",
        ".....#########++",
        "......########++",
    ], "texture": "gloss"},
    "Parka": {"half": [
        "..........######",
        "........##ffffff",
        ".......##ff11111",
        "......##ff111111",
        "......##ff111111",
        "....####ff111111",
        "..######fff11111",
        ".########ffff111",
        "#####x####ffffff",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#########n",
        "#####x#xxxxx###n",
        "#####x#+++++###n",
        "#####x#%%%%%###n",
        "#####x#%%%%%###n",
        "#####x#########n",
        "+++++x#########n",
        "+++++x#########n",
        ".....##########n",
        ".....##########n",
        ".....##########n",
        "......#########n",
    ], "texture": "quilt", "stamps": [(10, 9, ["m"]), (21, 9, ["m"])]},
    "Suit Jacket": {"half": [
        ".......#####ssss",
        ".....######+sssk",
        "...#######++sssk",
        "..###x####+++ssk",
        ".####x#####+++sk",
        "#####x######++sk",
        "#####x######++sk",
        "#####x#######+sk",
        "#####x#######+sk",
        "#####x########+k",
        "#####x#########m",
        "#####x#########x",
        "#####x#########x",
        "#####x#########m",
        "#####x#########x",
        "#####x#xxxxx###x",
        "#####x#+++++###x",
        "#####x#########x",
        "#####x#########x",
        "#m#m#x########x.",
        "......#######x..",
        "......######x...",
    ], "stamps": [(8, 6, ["s s"]), (7, 7, ["xxxxx"])]},
    # --- Headwear ------------------------------------------------------------------------
    "Baseball Cap": {"half": [
        "...............m",
        "..........#####x",
        "........#######x",
        "......#########x",
        ".....##########x",
        "....##n########x",
        "...####x#######x",
        "...####x#######x",
        "..####x########x",
        "..####x########x",
        ".+++++++++++++++",
        "++++++++++++++++",
        "++++++++++++++++",
        ".+++++++++++++++",
        "...1111111111111",
    ], "stamps": [(11, 3, ["5"]), (10, 4, ["5"])]},
    "Beanie": {"half": [
        "............++++",
        "...........+++++",
        "...........+++++",
        "............++++",
        "........########",
        "......##########",
        ".....###########",
        "....############",
        "...#############",
        "...#############",
        "..##############",
        "..##############",
        "..##############",
        ".rrrrrrrrrrrrrrr",
        ".rrrrrrrrrrrrrss",
        ".rrrrrrrrrrrrrss",
        ".rrrrrrrrrrrrrrr",
        "..rrrrrrrrrrrrrr",
    ], "texture": "knit"},
    "Bucket Hat": {"half": [
        "........########",
        ".......#########",
        "......##########",
        "......##########",
        ".....###########",
        ".....###########",
        ".....+++++++++++",
        ".....+++++++++++",
        "..%%%%%%%%%%%%%%",
        ".%%%%%%%%%%%%%%%",
        "%%%%%%%%%%%%%%%%",
        "%xxxxxxxxxxxxxxx",
        ".%%%%%%%%%%%%%%%",
    ], "stamps": [(7, 3, ["n"]), (24, 3, ["n"])]},
}

CATEGORY_DEFAULT = {"Top": "T-Shirt", "Bottom": "Jeans", "Footwear": "Sneakers",
                    "Socks": "Crew Socks", "Outerwear": "Jacket", "Headwear": "Baseball Cap"}

# Logo (Kleiderbügel) als 16x16-Zeichenraster: L = Linie.
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


# --- Raster aufbauen -------------------------------------------------------------------

def _round_corners(rows):
    """Entfernt äußere Eckpixel von Flächen, damit die Formen weicher wirken."""
    h, w = len(rows), len(rows[0])

    def empty(x, y):
        return not (0 <= x < w and 0 <= y < h) or rows[y][x] == "."

    corners = []
    for y in range(h):
        for x in range(w):
            if rows[y][x] not in PANELS + "r":
                continue
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                if (empty(x + dx, y) and empty(x, y + dy) and not empty(x - dx, y)
                        and not empty(x, y - dy) and not empty(x - 2 * dx, y) and not empty(x, y - 2 * dy)):
                    corners.append((x, y))
                    break
    for x, y in corners:
        rows[y][x] = "."


def grid(name):
    """Zentriertes 32x32-Zeichenraster eines Icons (Liste von Strings)."""
    spec = ICONS[name]
    if "half" in spec:
        for row in spec["half"]:
            assert len(row) == 16, f"{name}: half row has {len(row)} chars: {row!r}"
        rows = [list(row + row[::-1]) for row in spec["half"]]
    else:
        for row in spec["rows"]:
            assert len(row) <= SIZE, f"{name}: row too long: {row!r}"
        rows = [list(row.ljust(SIZE, ".")) for row in spec["rows"]]
    for x0, y0, lines in spec.get("stamps", []):
        for dy, line in enumerate(lines):
            for dx, ch in enumerate(line):
                if ch != " ":
                    rows[y0 + dy][x0 + dx] = ch
    if spec.get("round", True):
        _round_corners(rows)
    cells = [(y, x) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != "."]
    ys, xs = [y for y, _ in cells], [x for _, x in cells]
    h, w = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
    assert h <= SIZE and w <= SIZE, f"{name}: {w}x{h} does not fit"
    top, left = (SIZE - h) // 2, (SIZE - w) // 2
    out = [["."] * SIZE for _ in range(SIZE)]
    for y, x in cells:
        out[y - min(ys) + top][x - min(xs) + left] = rows[y][x]
    return ["".join(r) for r in out]


def _texture(name, x, y):
    """-1 (dunkler), 0 oder +1 (heller) für eine Zelle der Hauptfläche."""
    if name == "denim":
        return -1 if (x + y) % 3 == 0 else 0
    if name == "knit":
        return -1 if (x % 4 in (0, 3)) == (y % 2 == 0) else 0
    if name == "rib":
        return -1 if x % 3 == 0 else 0
    if name == "stripes":
        return -1 if y % 4 < 2 else 0
    if name == "quilt":
        return -1 if y % 4 == 0 else (1 if y % 4 == 1 else 0)
    if name == "gloss":
        return 1 if (x + y) % 12 == 0 and x < SIZE // 2 else 0
    if name == "fleece":
        return 1 if (x * 7 + y * 13) % 29 == 0 else 0
    if name == "mesh":
        return -1 if x % 2 == 0 and y % 2 == 0 else 0
    if name == "ripstop":
        return -1 if (x % 5 == 0 or y % 5 == 0) and (x + y) % 2 == 0 else 0
    return 0


def shades(name):
    """32x32-Raster mit Stufen 1-5 (int) bzw. festen Farbbuchstaben, None = leer."""
    g = grid(name)
    texture = ICONS[name].get("texture")

    def at(x, y):
        return g[y][x] if 0 <= x < SIZE and 0 <= y < SIZE else "."

    out = [[None] * SIZE for _ in range(SIZE)]
    for y in range(SIZE):
        for x in range(SIZE):
            c = g[y][x]
            if c == ".":
                continue
            if c in PANELS:
                down, right, up, left = at(x, y + 1), at(x + 1, y), at(x, y - 1), at(x - 1, y)
                if down == ".":
                    v = 1
                elif right == ".":
                    v = 2
                elif down != c or right != c:
                    v = 2
                elif up == "." and left == ".":
                    v = 5
                elif up != c or left != c:
                    v = 4
                elif at(x, y + 2) == "." or at(x + 2, y) == ".":
                    v = 2
                else:
                    v = 3
                if c == "#" and texture and v in (3, 4):
                    v = max(1, min(5, v + _texture(texture, x, y)))
                out[y][x] = v
            elif c == "r":
                out[y][x] = 1 if at(x, y + 1) == "." else (3 if x % 2 == 0 else 2)
            elif c == "x":
                out[y][x] = 2
            elif c in "12345":
                out[y][x] = int(c)
            elif c == "f":
                out[y][x] = "f" if (x * 5 + y * 3) % 4 else "S"
            else:
                out[y][x] = c
    return out


# --- Farben ------------------------------------------------------------------------------

def _mix(color, target, amount):
    c, t = QColor(color), QColor(target)
    return QColor(round(c.red() + (t.red() - c.red()) * amount),
                  round(c.green() + (t.green() - c.green()) * amount),
                  round(c.blue() + (t.blue() - c.blue()) * amount))


def ramp(fill):
    """Fünf Stufen aus der Teilfarbe. Sehr dunkle Farben werden leicht aufgehellt,
    sehr helle leicht abgedunkelt, damit Licht und Schatten sichtbar bleiben."""
    c = QColor(fill)
    lum = (0.2126 * c.red() + 0.7152 * c.green() + 0.0722 * c.blue()) / 255
    if lum < 0.15:
        base = _mix(fill, "#FFFFFF", 0.20)
    elif lum > 0.8:
        base = _mix(fill, "#000000", 0.10)
    else:
        base = c
    return {1: _mix(base, "#000000", 0.42), 2: _mix(base, "#000000", 0.20), 3: base,
            4: _mix(base, "#FFFFFF", 0.20), 5: _mix(base, "#FFFFFF", 0.48)}


def _luminance(color):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    c = QColor(color)
    return 0.2126 * lin(c.red()) + 0.7152 * lin(c.green()) + 0.0722 * lin(c.blue())


def needs_outline(fill):
    """True, wenn die Grundfarbe des Icons zu wenig Kontrast zur Kachel hat (WCAG-Kontrastverhältnis)."""
    a, b = _luminance(ramp(fill)[3]), _luminance(TILE)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05) < MIN_CONTRAST


def resolve(subcategory, category=None):
    """Name des Icons: die Subcategory, sonst das Standard-Icon der Category."""
    if subcategory in ICONS:
        return subcategory
    return CATEGORY_DEFAULT.get(category, "T-Shirt")


def render(subcategory, fill="#8E9296", dim=False, category=None):
    """32x32-Bild des Icons. dim=True: blasse Variante (leerer Slot, gelöschtes Teil)."""
    name = resolve(subcategory, category)
    colors = ramp(DIM_BASE if dim else fill)
    image = QImage(SIZE, SIZE, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    cells = shades(name)
    for y, row in enumerate(cells):
        for x, v in enumerate(row):
            if v is None:
                continue
            color = colors[v] if isinstance(v, int) else QColor(FIXED[v])
            if dim and not isinstance(v, int):
                color = _mix(color, DIM_BASE, 0.75)
            image.setPixelColor(x, y, color)
    if not dim and needs_outline(fill):
        line = _mix(colors[3], "#C4C8CC", 0.55)
        for y in range(SIZE):
            for x in range(SIZE):
                if cells[y][x] is None and any(0 <= x + dx < SIZE and 0 <= y + dy < SIZE
                                               and cells[y + dy][x + dx] is not None
                                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    image.setPixelColor(x, y, line)
    return image


def render_logo(background=False):
    image = QImage(16, 16, QImage.Format_ARGB32)
    image.fill(QColor(BG) if background else Qt.transparent)
    for r, row in enumerate(LOGO):
        for c, ch in enumerate(row):
            if ch == "L":
                image.setPixelColor(c, r, QColor(ACCENT))
    return image


def _scaled(image, scale):
    return QPixmap.fromImage(image).scaled(image.width() * scale, image.height() * scale,
                                           Qt.KeepAspectRatio, Qt.FastTransformation)


def pixmap(subcategory, fill="#8E9296", scale=3, dim=False, category=None):
    return _scaled(render(subcategory, fill, dim, category), scale)


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
