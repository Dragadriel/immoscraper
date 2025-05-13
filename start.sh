#!/bin/bash

echo "Installiere Chromium für Playwright..."
playwright install chromium

echo "Starte Immobotscript..."
python main.py
