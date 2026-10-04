# Klamotten Kurator (Gruppe 8)

Uniprojekt "Strukturiertes Programmieren" von Tomasz Karol Las (Tom), Nikolaus Koch (Niko) und Leopold Rolf Alfred Reinecke (Leo).
Die App schlägt aus dem eigenen digitalen Kleiderschrank ein Outfit vor. Arbeitssprache im Team: Deutsch.

## Festgelegte Rahmenbedingungen
- Python (unter Windows über `py` starten, `python` ist der Store-Alias), Entwicklung in VS Code.
- Datenbank: JSON-Flatfile `clothing_curator_dataset.json` (45 Teile, Liste von Objekten).
- GUI: **PySide6** (`pip install PySide6`), rein textbasiert, keine Bilder. **Alle Begriffe und Optionen in der GUI sind Englisch**, abgeleitet von den Attributnamen der JSON.
- Es wird immer nur **ein** Outfit angezeigt, dazu ein Button "anderes Outfit".
- Die App soll Kleidungsstücke über einfache Buttons hinzufügen können, z. B. Pants → Blue → Casual/Formal → Summer/Spring.

## Datenformat (ein Teil)
`Clothing_ID` ("C001"), `Name`, `Color`, `Occasion` (Liste), `Category`, `Subcategory`, `Season` (Liste).
- Season: Spring, Summer, Autumn, Winter.
- Occasion: Casual, Formal, Sport.
- Category: Top, Bottom, Footwear, Outerwear, Headwear, Socks (Socks ist vorbereitet, aber noch nicht in den Daten).
- Color: White, Black, Grey, Beige, Cream, Navy, Brown, Blue, Light Blue, Olive Green, Burgundy.
- Neue Farben müssen in `wardrobe.py` als neutral oder mit Farbton eingeordnet werden, sonst lehnt der Loader sie ab.

## Ablauf der App
Der Nutzer wählt ein Kleidungsstück, eine Season und eine Occasion. Der Algorithmus liefert ein Outfit mit den Slots Footwear, Socks, Bottom, Top, Outerwear (bei einer Kopfbedeckung als Ausgangsteil zusätzlich Headwear). Fehlt für einen Slot ein passendes Teil, gibt es für diesen Slot keinen Vorschlag.

## Stand der Dateien
- `wardrobe.py`: Konstanten, `load_wardrobe()` mit Validierung (wirft `ClothingDataError`), `save_wardrobe()` (atomar), `next_id()`, `add_item()` (vergibt ID, validiert, speichert). **Noch offen:** Bearbeiten und Löschen (FR2).
- `outfit_engine.py`: `suggest_outfit(wardrobe, anchor_id, season, occasion, exclude=(), rng=None)` gibt ein `Outfit` zurück (`slots`, `score`, `format()`). Kommandozeilen-Test: `py outfit_engine.py C016 Autumn Casual`.
- `clothing_curator_dataset.json`: die aktuelle Datenbasis.
- `kleiderschrank.json`: älterer deutscher Entwurf, wird nirgends verwendet, kann gelöscht werden.
- **Noch nicht vorhanden:** die GUI. Das Mockup steht aus.

## Algorithmus (Entscheidungen)
1. **Harte Filter:** Ein Teil muss zur gewählten Season UND zur gewählten Occasion passen.
2. **Gewichtung:** Season 50, Occasion 30, Color 20 (max. 100 Punkte), entsprechend der Vorgabe "zuerst Season, dann Occasion, dann Farben".
3. **Spezialisierung:** Je weniger Seasons/Occasions ein Teil hat, desto besser passt es. Season: 1 Season = 1.0, 4 Seasons = 0.25. Occasion: 1 = 1.0, 2 = 0.67, 3 = 0.33.
4. **Farblehre:** neutral + neutral = 1.0, neutral + Farbe = 0.9, ähnlicher Farbton (bis 45°) = 0.85, Kontrast (ab 120°) = 0.8, sonst 0.4. Ein Outfit bekommt den Durchschnitt über alle Paare.
5. **Performance:** Pro Slot werden nur die besten 8 Kandidaten kombiniert (500 Teile, 12 Vorschläge in ca. 0,04 s).
6. **Gleichstand:** Outfits innerhalb von 3 Punkten zum Besten gelten als gleich gut, dann entscheidet der Zufall. `exclude` mit `Outfit.key` ermöglicht "anderes Outfit".
7. **Passt das Ausgangsteil selbst nicht zu Season/Occasion**, wird es trotzdem verwendet, aber mit einem Hinweis in `Outfit.warnings` (die GUI könnte die Auswahl stattdessen vorab filtern).

## Bekannte Lücken und offene Punkte
- In den Daten gibt es keine Socken, die Socken-Zeile ist daher immer leer. Es müssen Socken ergänzt werden (z. B. mit `add_item`).
- Im Sommer gibt es nie eine Jacke, weil keine Jacke die Season "Summer" hat. Das ist gewollt.
- Die harten Filter und die Farbwerte sind von mir vorgeschlagen und vom Team noch nicht ausdrücklich bestätigt.
- Es gibt noch keine automatischen Tests, geprüft wurde per Skript auf einer Kopie der Daten.
- Optionale Anforderungen (OF1 Temperatur, OF2 Wäschewarnung, OF3 Kalendereintrag) sind nicht begonnen.

## Anforderungen aus der Projektbeschreibung
- FR1/FR2 (Tom): Teile über Buttons aufnehmen, bearbeiten, löschen.
- FR3/FR4 (Niko): Teil oder Situation als Ausgangspunkt wählen, Outfit erstellen.
- FR5/FR6 (Leo): Season, Farbe und Kleidungsart berücksichtigen, Style-Ergänzungen für den Schrank vorschlagen.
- NFR1: grafische Oberfläche ohne Kommandozeile. NFR2: Outfit in unter 2 s bei bis zu 500 Teilen. NFR3: Daten bleiben nach Neustart erhalten.

## Git-Stand
Das Repository ist lokal und hat noch keinen Commit und kein Remote. Zum Teilen mit dem Team und zwischen den Rechnern wäre ein GitHub-Repository sinnvoll.

## Nächste Schritte
1. Mockup der GUI ansehen, dann die GUI mit PySide6 bauen (Auswahl: Teil, Season, Occasion; Ausgabe: Outfit-Text; Button "anderes Outfit"; Formular zum Hinzufügen per Buttons).
2. Socken in die Daten aufnehmen.
3. Bearbeiten und Löschen in `wardrobe.py` ergänzen.
4. Erster Commit und gemeinsames Repository.
