# OFE-Datenfusion – QGIS Plugin für On-Farm-Experimente

Das OFE Datenfusion Plugin ist das dritte Plugin des OFE-Werkzeugkastens der OG SNaPwürZ. Es erweitert QGIS um leistungsstarke Interpolationsverfahren für Raster- und Punktdaten sowie weitere Methoden für die räumliche Zusammenführung von Geodaten. Es bietet mehrere Interpolationsmethoden, interaktive Variogramm-Analyse, automatische UTM-Konvertierung und eine deutschsprachige Benutzeroberfläche.

---

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Interpolationsmethoden](#interpolationsmethoden)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Voraussetzungen](#voraussetzungen)
- [Verzeichnisstruktur](#verzeichnisstruktur)
- [Output-Struktur](#output-struktur)
- [Support & Kontakt](#support--kontakt)
- [Lizenz](#lizenz)

---

## 🎯 Überblick

Das Plugin unterstützt Interpolation für typische Datenszenarien in On-Farm-Experimenten – von Raster-Interpolation (flächendeckende Karten) bis zur Punkt-Interpolation (Anreicherung/ Schätzung auf vorgegebene Koordinaten).

### Hauptfunktionen auf einen Blick

- ✅ **Raster-Interpolation** – Erzeugt Rasterkarten aus Punktdaten
- ✅ **Punkt-Interpolation** – Schätzt Werte an vorgegebenen Koordinaten eines Punkt-Layers
- ✅ **Automatische UTM-Konvertierung** – UTM-Zone erkennen & konvertieren
- ✅ **Variogramm-Analyse** (für Kriging) – Interaktiv analysieren & optimieren

---

## ✨ Features

### Interpolation
- Ordinary Kriging, IDW und Nearest Neighbor
- Flexible Rasterauflösung
- Punkt-zu-Punkt Interpolation zur Datensatzanreicherung
- Automatische Variogramm-Parameter-Optimierung
- Optionale Kriging-Varianz (σ²) als zusätzliche Karte

### Variogramm-Analyse (nur Kriging)
- Experimentelles und theoretisches Variogramm
- Modellvergleich: Linear, Spherical, Exponential, Gaussian
- RMSE- und R²-Berechnung für Modellvalidierung
- Automatische Parameteroptimierung mit grüner Spinbox-Markierung

### Datenverarbeitung
- Automatische UTM-Zonenerkennung und -Konvertierung
- Validierung von Eingabedaten und Geometrien
- Unterstützung von Begrenzungspolygonen (Boundary Clipping)
- Behandlung von Multi-Part-Geometrien
- Duplikat-Koordinaten-Erkennung mit Averaging-Option

### Benutzerfreundlichkeit
- Interaktive Benutzeroberfläche mit Tab-System
- Dialog bleibt nach Interpolation offen für Folgeanalysen
- Optionale Vektor-Layer Ausgabe
- Automatisches Farbrampen-Styling (Rot-Gelb-Grün)
- Ausführliche Fehlerbehandlung und Logging
- Deutsche Benutzerführung

---

## 🧮 Interpolationsmethoden

| Methode | Beschreibung | Bibliothek |
|---------|--------------|------------|
| **Ordinary Kriging** | Geostatistische Interpolation mit Variogramm-Analyse | PyKrige (optional) |
| **IDW** | Inverse Distance Weighting – distanzgewichtete Interpolation | QGIS-nativ |
| **Nearest Neighbor** | Nächster-Nachbar-Zuweisung ohne Glättung | GDAL |

---

## 🧩 Installation

### Option A (empfohlen): Installation über QGIS-Plugin-Repository (Auto-Updates)
> Hier gehts zum ausführlichen Tutorial: [Installation der SNaPWürZ Plugins für QGIS](https://farmwiki.de/de/Tutorials/GIS/QGIS/installation_snapwuerz_plugin)
1. QGIS öffnen
2. **Erweiterungen → Erweiterungen verwalten und installieren…**
3. Reiter **Einstellungen**
4. Sicherstellen, dass **Auch experimentelle Erweiterungen anzeigen** aktiviert ist
5. Unter **Erweiterungsrepositorien** auf **Hinzufügen…** klicken
5. Name vergeben (z. B. `SNaPwürZ OFE-Datenfusion`) und folgende URL eintragen:

   `https://github.com/FARMWISSEN/OFE-Datenfusion/releases/latest/download/plugins.xml`

6. Mit **OK** bestätigen und **Repos aktualisieren** / **Neu laden**
7. Reiter **Alle** (oder Suche) → **OFE-Datenfusion** auswählen → **Installieren**


### Option B: Manuelle Installation aus dem Quellcode (für Entwicklung)
Diese Variante ist für Entwickler gedacht.

1. Repository klonen oder herunterladen
2. Sicherstellen, dass der Plugin-Ordner **`ofe_datenfusion/`** direkt im QGIS-Plugin-Verzeichnis liegt:

   Windows (Standardprofil):
   `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\ofe_datenfusion`

3. QGIS neu starten und Plugin im Plugin-Manager aktivieren

### Optionale Abhängigkeit: PyKrige
PyKrige wird nur für **Kriging** benötigt. **IDW** und **Nearest Neighbor** funktionieren auch ohne PyKrige.
> Hier gehts zum ausführlichen Tutorial: [Installation von Python-Paketen in der Python-Umgebung von QGIS](https://farmwiki.de/de/Tutorials/GIS/QGIS/installation_python_pakete_qgis)

**Windows (OSGeo4W Shell):**
```bash
python -m pip install pykrige
```

**Mac:**
```bash
/Applications/QGIS-LTR.app/Contents/MacOS/bin/pip3 install pykrige
```

> **Hinweis:** Ohne PyKrige wird Kriging automatisch deaktiviert und die entsprechenden UI-Elemente ausgeblendet.

---

## 🚀 Schnellstart

1. Öffne das Plugin: *Praxisversuche → OFE-Datenfusion*
2. Raster-Tab: Wähle Eingabe-Layer, Attributfeld und optional Boundary
3. Punkt-Tab: Wähle Kovariaten-Layer und Ziel-Layer
4. Führe optional eine Variogramm-Analyse durch (nur Kriging)
5. Klicke auf „Interpolieren“
6. Ergebnisse werden zur Layer-Gruppe „OFE-Datenfusion“ hinzugefügt

---

## 🧰 Voraussetzungen

- QGIS >= 3.x
- Python >= 3.7
- PyKrige (optional, nur für Kriging)

---

## 🗂️ Verzeichnisstruktur

```text
interpolation/
├── i_plugin.py                     # Hauptlogik: Dispatcher + Interpolations-Workflows
├── i_plugin_dialog.py              # UI-Controller: Dialog-Management
├── config.py                       # Zentrale Konfigurationskonstanten
├── exceptions.py                   # Custom Exception-Hierarchie
├── variogram_models.py             # Variogramm-Modelle
├── variogram_plotter.py            # Variogramm-Visualisierung
├── variogram_dialog.py             # Variogramm-Analyse Dialog
├── model_comparison_dialog.py      # Modellvergleich-Dialog
├── duplicate_coordinates_dialog.py # Duplikat-Behandlung Dialog
├── Optimierung.ui                  # Qt Designer UI-Datei
├── DEVELOPER_README.md             # Entwickler-Dokumentation
└── README.md
```

---

## 📦 Output-Struktur

```text
projektverzeichnis/
└── OFE_Datenfusion/
    ├── raster_interpolation/       # Raster-Ergebnisse (.tif)
    ├── point_interpolation/        # Punkt-Ergebnisse (.shp)
    ├── utm_layers/                 # UTM-transformierte Layer
    └── backups/                    # Automatische Backups
```

---

## 🆘 Support & Kontakt

- Fehler bitte als Issue melden: https://github.com/FARMWISSEN/OFE-Datenfusion/issues 
- Repository: https://github.com/FARMWISSEN/OFE-Datenfusion
- Projekthomepage: https://snapwürz.de/
![](https://xn--snapwrz-r2a.de/wp-content/uploads/2024/06/Logo_Transparent-1-1024x635.png)


---

## :dollar: Förderung
### Europäische Innovationspartnerschaft (EIP Agri)
Das Projekt **Chancen durch digitale Innovation in On Farm Research und Exaktversuchen** (SNaPwürZ) wird durch die EU im Rahmen der Europäischen Innovationspartnerschaft (EIP Agri) und das Landesprogramm Ländlicher Raum des Landes Schleswig-Holstein (LPLR) gefördert. Ziel ist es, neue Problemlösungen anzuregen, die die Nachhaltigkeit und Effizienz in der Landwirtschaft steigern. Jedes Projekt wird durch eine Operationelle Gruppe (OG) gesteuert. Darin arbeiten Landwirte, Wissenschaftler, Berater, NGOs und Wirtschaftspartner gemeinsam.

www.eip-agrar-sh.de 

---

## 📄 Lizenz

Dieses Projekt ist freie Software: Du kannst es unter den Bedingungen der **GNU General Public License** weiterverbreiten und/oder modifizieren, wie von der Free Software Foundation veröffentlicht; entweder **Version 2 der Lizenz** oder (nach deiner Wahl) **jeder späteren Version**.

Der vollständige Lizenztext liegt in der Datei **LICENSE.txt**.

**SPDX-License-Identifier:** `GPL-2.0-or-later`
