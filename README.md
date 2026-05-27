# OFE-Planung – QGIS Plugin für die Planung von On-Farm-Experimenten

Das OFE Planung Plugin ist ein Plugin des OFE-Werkzeugkastens der OG SNaPwürZ. Es unterstützt in QGIS bei der digitalen Planung von On-Farm-Experimenten – von Streifenversuchen über Kleinparzellen bis zur Erstellung von Kernparzellen, Exportdaten und druckfertigen PDF-Karten. Das Plugin bietet eine deutschsprachige Benutzeroberfläche, automatische UTM-Konvertierung, interaktive AB-Linien-Zeichnung und strukturierte Ausgabe von Versuchsparzellen als Geodaten.

---

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Planungsmodule](#planungsmodule)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Voraussetzungen](#voraussetzungen)
- [Verzeichnisstruktur](#verzeichnisstruktur)
- [Output-Struktur](#output-struktur)
- [Support & Kontakt](#support--kontakt)
- [Förderung](#dollar-förderung)
- [Lizenz](#lizenz)

---

## 🎯 Überblick

Das Plugin unterstützt die Planung typischer Versuchsanlagen in On-Farm-Experimenten. Aus Feldgrenzen, optionalen Vorgewenden, Lenkspuren und Ausschlussflächen können Versuchsparzellen erzeugt, randomisiert, als Layer gespeichert und für die Weiterverarbeitung exportiert werden.

### Hauptfunktionen auf einen Blick

- ✅ **Streifenversuche planen** – Parzellen entlang einer interaktiv gezeichneten AB-Linie erstellen
- ✅ **Kleinparzellen planen** – Rasterförmige Parzellen mit Breite, Länge, Anzahl und Abständen erzeugen
- ✅ **Kernparzellen erzeugen** – Netto-/Kernparzellen innerhalb vorhandener Versuchsparzellen ableiten
- ✅ **Automatische UTM-Konvertierung** – UTM-Zone erkennen & Layer für metrische Planung reprojizieren
- ✅ **Randomisierung** – Varianten und Wiederholungen automatisch auf Parzellen verteilen
- ✅ **Export & Druck** – Ausgewählte Layer als ZIP exportieren und Versuchskarte als PDF erstellen

---

## ✨ Features

### Versuchsplanung
- Erfassung von Versuchsfragestellung, Versuchsjahr, Faktoren und Faktorstufen
- Unterstützung von ein- und zweifaktoriellen Versuchsanlagen
- Automatische Bildung von Varianten aus Faktorstufen
- Planung von Streifenversuchen mit Parzellenbreite und Wiederholungen
- Planung von Kleinparzellen mit Parzellenbreite/-länge, Anzahl X/Y und Parzellenabständen
- Interaktive AB-Linie zur Ausrichtung der Versuchsanlage

### Geodatenverarbeitung
- Automatische UTM-Zonenerkennung anhand der Feldgrenze
- Reprojektion von Feldgrenzen, Lenkspuren und Ausschlussflächen in ein metrisches Ziel-KBS
- Optionales Zuschneiden eines Vorgewendes mit separater Innerfläche
- Clipping der Parzellen auf Feldgrenze oder Innerfläche
- Abzug von Ausschlussflächen aus der Parzellengeometrie
- Validierung von Eingabe-Layern nach Geometrietyp

### Randomisierung & Styling
- Zufällige Zuordnung von Varianten innerhalb der Wiederholungen
- Attributierung der Parzellen mit ID, Label, Wiederholung, Faktor(en) und Variante
- Kategorisiertes Styling nach Variante
- Automatische Beschriftung über das Feld `LABEL`
- Layer-Gruppe „Versuchsplanung“ für übersichtliche Projektstruktur

### Kernparzellen
- Erstellung von Kernparzellen aus bestehenden Versuchsparzellen
- Einstellbare Kernbreite und Kernlänge
- Platzierung in der Mitte, am unteren Ende (A) oder am oberen Ende (B) der Parzelle
- Übernahme der Variantenattribute aus dem Parzellen-Layer
- Optionales Laden von Kernparzellen-Parametern aus JSON

### Export & Druck
- Speichern der Planung als Shapefiles und `ofe_parameter.json`
- Wiederherstellung gespeicherter Planungsparameter und Layer beim erneuten Öffnen
- Export ausgewählter Layer als ZIP-Datei mit Shapefile-Bestandteilen
- Export-Layer werden für die Weitergabe nach EPSG:4326 transformiert
- PDF-Druck mit DIN A4/A3, Hoch-/Querformat, Legende, Maßstab und Nordpfeil
- OpenStreetMap-Hintergrund im integrierten Kartenfenster

### Benutzerfreundlichkeit
- Deutschsprachige Benutzeroberfläche
- Tab-basierter Workflow: Fragestellung → Planung → Kernparzellen → Druck/Export
- Integriertes Kartenfenster zur direkten Kontrolle der Planung
- Snapping beim Zeichnen der AB-Linie
- Projektbezogener Arbeitsordner im QGIS-Projektverzeichnis
- Ausführliche Fehlermeldungen und Logging

---

## 🧭 Planungsmodule

| Modul | Beschreibung | Ausgabe |
|-------|--------------|---------|
| **Streifenversuch** | Erstellt parallel ausgerichtete Versuchsparzellen entlang einer AB-Linie | Polygon-Layer `Versuchsparzellen` |
| **Kleinparzellen** | Erstellt eine rechteckige Parzellenanlage mit definierter Anzahl, Größe und Abständen | Polygon-Layer `Versuchsparzellen` |
| **Vorgewende** | Erzeugt innere Nutzfläche und Vorgewende aus der Feldgrenze | Polygon-Layer `Innerfläche`, `Vorgewende` |
| **Kernparzellen** | Leitet Kern-/Netto-Parzellen aus vorhandenen Parzellen ab | Polygon-Layer `<präfix>plots` |
| **Export** | Packt ausgewählte Layer als Shapefiles in eine ZIP-Datei | ZIP-Datei, EPSG:4326 |
| **Druck** | Erstellt eine druckfertige Versuchskarte | PDF-Datei |

---

## 🧩 Installation

### Option A (empfohlen): Installation über QGIS-Plugin-Repository (Auto-Updates)
> Hier gehts zum ausführlichen Tutorial: [Installation der SNaPWürZ Plugins für QGIS](https://farmwiki.de/de/Tutorials/GIS/QGIS/installation_snapwuerz_plugin)

1. QGIS öffnen
2. **Erweiterungen → Erweiterungen verwalten und installieren…**
3. Reiter **Einstellungen** öffnen
4. Sicherstellen, dass **Auch experimentelle Erweiterungen anzeigen** aktiviert ist
5. Unter **Erweiterungsrepositorien** auf **Hinzufügen…** klicken
6. Name vergeben (z. B. `SNaPwürZ OFE-Planung`) und die Repository-URL des GitLab-Releases eintragen
7. Mit **OK** bestätigen und **Repos aktualisieren** / **Neu laden**
8. Reiter **Alle** (oder Suche) → **OFE Planning** auswählen → **Installieren**

> **Hinweis:** Falls noch keine `plugins.xml` über GitLab Releases bereitgestellt wird, nutze Option B für die manuelle Installation.

### Option B: Manuelle Installation aus dem Quellcode (für Entwicklung)
Diese Variante ist für Entwickler gedacht.

1. Repository klonen oder herunterladen
2. Sicherstellen, dass der Plugin-Ordner **`ofe_planning/`** direkt im QGIS-Plugin-Verzeichnis liegt:

   Windows (Standardprofil):
   `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\ofe_planning`

   Linux (Standardprofil):
   `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/ofe_planning`

   macOS (Standardprofil):
   `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/ofe_planning`

3. Falls Ressourcen geändert wurden, Ressourcen neu kompilieren:

```bash
pyrcc5 -o resources.py resources.qrc
```

4. QGIS neu starten und Plugin im Plugin-Manager aktivieren

---

## 🚀 Schnellstart

1. QGIS-Projekt speichern – das Plugin benötigt ein gespeichertes Projektverzeichnis
2. Öffne das Plugin: *Praxisversuche → OFE Planung*
3. Tab **1. Fragestellung**: Versuchsfragestellung, Versuchsjahr, Faktoren und Faktorstufen eingeben
4. **OFE planen** oder **Kleinparzellen planen** auswählen
5. Feldgrenze laden und optional Vorgewende, Lenkspuren und Ausschlussflächen übernehmen
6. **Linie zeichnen** anklicken und die AB-Linie im Kartenfenster setzen
7. **Parzellen anlegen** und anschließend **Randomisieren** ausführen
8. Planung über **Speichern** sichern
9. Optional im Tab **Kernparzellen** Kernparzellen erzeugen
10. Im Tab **Drucken / Exportieren** Layer als ZIP exportieren oder PDF-Karte erstellen

---

## 🧰 Voraussetzungen

- QGIS >= 3.x
- Python >= 3.7 innerhalb der QGIS-Python-Umgebung
- Gespeichertes QGIS-Projekt vor Start des Plugins
- Eingabe-Layer:
  - Feldgrenze als Polygon-Layer
  - Lenkspur(en) als Linien-Layer (optional)
  - Ausschlussflächen als Polygon-Layer (optional)

> **Hinweis:** Das Plugin nutzt QGIS-/PyQGIS-Funktionen und QGIS Processing. Zusätzliche externe Python-Pakete sind für die Kernfunktionen nicht erforderlich.

---

## 🗂️ Verzeichnisstruktur

```text
ofe_planning/
├── ofe_planning.py              # Plugin-Einstieg: Menü, Toolbar, Dialogstart
├── ofe_planning_dialog.py       # UI-Controller und Planungs-Workflows
├── ofe_planning_dialog_base.ui  # Qt Designer UI-Datei
├── ofe_planning_maptool.py      # Kartenwerkzeug für AB-Linie und Parzellenvorschau
├── generate_blocks.py           # Block-/Parzellenlogik für Versuchsanlagen
├── generate_parallel_lines.py   # Erzeugung paralleler Linien entlang der AB-Ausrichtung
├── generate_core_plots.py       # Erstellung von Kernparzellen
├── crs_utils.py                 # UTM-Erkennung und Reprojektion
├── layer_manager.py             # Layer-Validierung, Speicherung und ZIP-Export
├── styling.py                   # Symbolisierung und Varianten-Styling
├── constants.py                 # Zentrale Konfigurationswerte
├── enum_versuchstypen.py        # Versuchstypen und MapTool-Modi
├── metadata.txt                 # QGIS Plugin-Metadaten
├── resources.qrc                # Qt Resource Collection
├── resources.py                 # Kompilierte Ressourcen
├── icons/
│   └── north_arrow.svg          # Nordpfeil für PDF-Ausgabe
└── README.md
```

---

## 📦 Output-Struktur

```text
projektverzeichnis/
└── ofe_planung/
    ├── ofe_parameter.json              # Gespeicherte Planungsparameter und Layer-Pfade
    ├── Feld_<layer>_<id>.shp           # UTM-transformierte Feldgrenze
    ├── Lane_<layer>_<id>.shp           # UTM-transformierte Lenkspur(en)
    ├── AF_<layer>_<id>.shp             # UTM-transformierte Ausschlussflächen
    ├── Innerfläche.shp                 # Nutzfläche nach Vorgewende-Abzug
    ├── Vorgewende.shp                  # Vorgewende-/Randbereich
    ├── AB Line.shp                     # Gezeichnete AB-Linie
    ├── Versuchsparzellen.shp           # Randomisierte Versuchsparzellen
    ├── <präfix>plots.shp               # Optional erzeugte Kernparzellen
    ├── *.zip                           # Optionaler Export ausgewählter Layer
    └── *.pdf                           # Optional erzeugte Versuchskarte
```

> **Hinweis:** Shapefiles bestehen aus mehreren Dateien (`.shp`, `.dbf`, `.shx`, `.prj`, `.cpg`). Beim ZIP-Export werden die relevanten Bestandteile automatisch zusammengepackt.

---

## 🆘 Support & Kontakt

- Fehler bitte als Issue im GitLab-Repository dieses Plugins melden
- Repository: GitLab-Projekt **OFE Planning** 
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

Der vollständige Lizenztext sollte in der Datei **LICENSE.txt** im Repository abgelegt werden.

**SPDX-License-Identifier:** `GPL-2.0-or-later`
