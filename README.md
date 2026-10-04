# Klamotten Kurator

Die App schlägt aus dem eigenen digitalen Kleiderschrank ein Outfit vor.
Uniprojekt "Strukturiertes Programmieren", Gruppe 8. Die Oberfläche ist englisch.

## Windows

Die fertige `Klamottenkurator.exe` per Doppelklick starten, Python ist nicht nötig.
Bei der Warnung "Der Computer wurde durch Windows geschützt" auf **Weitere Informationen** und dann auf
**Trotzdem ausführen** klicken (die Datei ist nicht signiert).
Jeder Nutzer hat seinen eigenen Kleiderschrank unter `%APPDATA%\Klamottenkurator`.

## Linux und macOS

Die `.exe` läuft nur unter Windows. Auf Linux und macOS startest du die App aus dem Quellcode.

### 1. Voraussetzungen
- **Python 3.10 oder neuer** und `git`.
  - macOS: `brew install python` (oder der Installer von python.org).
  - Debian/Ubuntu: `sudo apt install python3 python3-venv python3-pip git`.
  - Fedora: `sudo dnf install python3 git`.
- Nur Linux, falls das Fenster nicht startet und die Meldung `xcb-cursor` erscheint:
  `sudo apt install libxcb-cursor0` (Debian/Ubuntu).

### 2. Code holen
```bash
git clone https://github.com/Baltrom/Klamottenkuratorv1.2.git
cd Klamottenkuratorv1.2
```

### 3. Virtuelle Umgebung anlegen und PySide6 installieren
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Die virtuelle Umgebung hält die Installation vom restlichen System getrennt.
In einem neuen Terminal musst du vorher wieder `source .venv/bin/activate` ausführen.

### 4. App starten
```bash
python3 gui.py
```

### Wo liegen meine Daten?
Beim Start aus dem Quellcode liegen Kleiderschrank (`clothing_curator_dataset.json`) und gespeicherte
Outfits (`saved_outfits.json`) im Projektordner. Wer einen eigenen, vom Repository getrennten Schrank
will, setzt vor dem Start einen eigenen Ordner:
```bash
KLAMOTTENKURATOR_DATA="$HOME/klamottenkurator" python3 gui.py
```
Beim ersten Start wird die mitgelieferte Datenbasis dorthin kopiert.

### Tests (optional)
```bash
pip install pytest
python3 -m pytest
```

### Eigene Programmdatei bauen (optional)
Eine Datei für das eigene System entsteht mit PyInstaller. Gebaut wird immer für das System, auf dem
man baut (ein Mac-Programm also nur auf einem Mac):
```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name Klamottenkurator \
  --add-data "clothing_curator_dataset.json:." gui.py
```
Das Ergebnis liegt in `dist/`. Beachte das `:` statt `;` vor dem Punkt, das gilt auf Linux und macOS.
Unter macOS kann Gatekeeper das Programm blockieren: Rechtsklick auf die Datei, **Öffnen**, bestätigen.

### Bekannte Einschränkungen
- Die Schrift "Bahnschrift" gibt es nur unter Windows. Auf Linux und macOS nimmt die App automatisch eine
  andere Systemschrift, das Aussehen weicht dann leicht ab.
- Die App wurde bisher nur unter Windows getestet. Wenn etwas nicht klappt, bitte die Fehlermeldung
  aus dem Terminal an das Team schicken.

## Kommandozeile (ohne Oberfläche, zum Testen)
```bash
python3 outfit_engine.py Autumn Casual --anchor C016   # mit Ausgangsteil
python3 outfit_engine.py Winter Formal                 # ohne Ausgangsteil
python3 outfit_engine.py Winter Casual --edgy          # inverse Bewertung
```
Unter Windows heißt der Python-Befehl `py`.

Details zu Datenformat und Algorithmus stehen in `CLAUDE.md`.
