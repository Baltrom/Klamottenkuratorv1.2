@echo off
rem Baut dist\Klamottenkurator.exe (einzelne Datei, kein Python noetig zum Starten).
rem Voraussetzung: py -m pip install PySide6 pyinstaller
cd /d "%~dp0"
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Klamottenkurator ^
  --add-data "clothing_curator_dataset.json;." gui.py
if errorlevel 1 exit /b 1
echo.
echo Fertig: dist\Klamottenkurator.exe
