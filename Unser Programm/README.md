# Klamotten Kurator — Editorial Minimal, Team-Datenmodell

## Start

ZIP in einen neuen Ordner entpacken. Im enthaltenen Projektordner:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Linux Mint: bei fehlendem venv `sudo apt install python3.12-venv`; bei xcb-Fehler `sudo apt install libxcb-cursor0`.
Windows: `python -m venv .venv` und `.venv\Scripts\activate` verwenden.

## Eure Werte

Die mitgelieferte `wardrobe.py` ist unverändert übernommen. Kategorien/Unterkategorien, Farben, Anlässe und Jahreszeiten stammen direkt daraus. Kategorien werden in der Oberfläche deutsch beschriftet, intern bleiben die englischen Werte erhalten. Die übrigen Auswahlwerte erscheinen wie in eurer Datei.

JSON enthält eine Liste mit den Feldern `Clothing_ID`, `Name`, `Color`, `Occasion`, `Category`, `Subcategory`, `Season`. Neue IDs und Namen erzeugt `wardrobe.add_item`; Laden und Speichern verwenden eure Funktionen.

## Datensatz laden

Die hochgeladene Python-Datei enthält Definitionen, noch keine Kleidungsstücke. Ohne Datensatz startet der Kleiderschrank leer. Auf der Startseite „JSON-Kleiderschrank importieren“ anklicken (bei kleinerem Fenster nach unten scrollen). Der Import ergänzt vorhandene Teile, überspringt identische Einträge und bricht bei widersprüchlichen IDs ab. Die ausgewählte Quelldatei bleibt unverändert.

Alternativ `clothing_curator_dataset.json` neben `main.py` legen, bevor die App startet. Dann nutzt die App diese Projektdatei direkt; hinzugefügte Kleidung wird darin gespeichert. Ohne Projektdatei verwendet sie den Benutzer-App-Datenordner. Die alte Prototypdatei `wardrobe.json` wird nicht verändert oder automatisch migriert.

## Outfit-Prototyp

Anlass und Jahreszeit müssen übereinstimmen. Neutrale Farben aus `wardrobe.NEUTRAL_COLORS` oder die Basisfarbe werden bevorzugt. Ein vollständiges Outfit umfasst Top, Bottom und Footwear; eine gewählte andere Kategorie bleibt zusätzlich erhalten. Das Farbrad ist in eurer Datei definiert, konkrete Farbharmonie-Regeln jedoch nicht; diese Version verwendet die einfache Neutralfarben-Heuristik. Socken und Kopfbedeckung werden nur ergänzt, wenn sie als Basis gewählt sind.

Gespeicherte Kombinationen liegen separat in `saved_outfits.json`. Eine Ansicht dafür, Fotos sowie Bearbeiten/Löschen sind noch nicht implementiert. „Andere Kombination“ kann bei wenigen passenden Teilen dasselbe Ergebnis liefern.

## Geprüft

Alle sechs Kategorien, fünf Wizard-Schritte, Mehrfachauswahl, IDs, JSON-Feldnamen, Speichern/Laden, Outfit-Erstellung und Import ohne Änderung der Quelldatei wurden mit Qt im Offscreen-Modus geprüft.
