# Fehlerbehandlung und Problemlösung

## Häufige PDF-Probleme und Lösungen

### 1. Korrupte PDF-Struktur (NullObject Error)

**Fehlermeldung:**
```
Korrupte PDF-Struktur in 'dokument.pdf'
  Pfad: /vollständiger/pfad/dokument.pdf
  Größe: 123,456 Bytes
  Problem: PDF enthält ungültige Objekte
  Tipp: Datei mit Adobe/Preview reparieren und neu speichern
```

**Ursache:** Die PDF-Datei enthält interne Strukturfehler (ungültige oder fehlende Objekte).

**Lösung:**
1. Öffnen Sie die Datei in Adobe Acrobat oder macOS Preview
2. Speichern Sie die Datei unter neuem Namen (Datei → Exportieren als PDF)
3. Verwenden Sie die reparierte Version

**Alternative:** Nutzen Sie Online-Tools wie:
- https://www.ilovepdf.com/repair-pdf
- Ghostscript: `gs -o fixed.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress corrupt.pdf`

---

### 2. Leere Dateien (0 Bytes)

**Fehlermeldung:**
```
Skipping empty file: dokument.pdf (0 bytes)
```

**Ursache:** Die Datei ist leer oder der Download wurde unterbrochen.

**Lösung:**
- Löschen Sie die leere Datei
- Laden Sie das Dokument erneut herunter
- Die Datei wird automatisch übersprungen und andere Dateien werden verarbeitet

---

### 3. Zu kleine Dateien (< 100 Bytes)

**Fehlermeldung:**
```
Skipping file (too small): dokument.pdf (45 bytes)
```

**Ursache:** Die Datei ist zu klein, um ein gültiges PDF zu sein.

**Lösung:**
- Prüfen Sie, ob die Datei korrekt heruntergeladen wurde
- Die Datei wird automatisch übersprungen

---

### 4. Passwortgeschützte PDFs

**Fehlermeldung:**
```
Geschützte PDF: 'dokument.pdf'
  Pfad: /vollständiger/pfad/dokument.pdf
  Problem: PDF ist passwortgeschützt
```

**Ursache:** Das PDF erfordert ein Passwort zum Öffnen.

**Lösung:**
1. Öffnen Sie die Datei mit dem Passwort
2. Speichern Sie eine ungeschützte Kopie
3. Verwenden Sie die ungeschützte Version

**Alternative:**
```bash
# Mit qpdf (macOS: brew install qpdf)
qpdf --password=PASSWORT --decrypt input.pdf output.pdf
```

---

### 5. Beschädigte/Unvollständige PDFs

**Fehlermeldung:**
```
Beschädigte PDF-Datei: 'dokument.pdf'
  Pfad: /vollständiger/pfad/dokument.pdf
  Größe: 123,456 Bytes
  Problem: Datei ist unvollständig oder beschädigt
```

**Ursache:** Die PDF-Datei wurde nicht vollständig heruntergeladen oder ist beschädigt.

**Lösung:**
1. Laden Sie die Datei erneut herunter
2. Reparieren Sie die Datei mit Adobe Acrobat
3. Nutzen Sie Ghostscript zur Reparatur (siehe oben)

---

## Automatisches Überspringen

Die Anwendung verarbeitet **automatisch weiter**, wenn einzelne Dateien Probleme haben:

- ✅ Leere Dateien werden übersprungen
- ✅ Zu kleine Dateien werden übersprungen
- ✅ Korrupte PDFs werden übersprungen
- ✅ Andere gültige PDFs im Ordner werden verarbeitet
- ⚠️ Am Ende wird eine Warnung mit übersprungenen Dateien angezeigt

**Beispiel-Log:**
```
[1/3] Processing folder: Posteingang
  Found 10 PDF files
  Skipped 1 previously joined PDF(s)
  Output: Posteingang_2026-01-06_14-30-45.pdf
  Merging PDFs (sorted by date, newest first)...
  ✓ Successfully merged 8 PDFs (reduced by 45.2 MB, 42.5%)
  ⚠ Warnung: Erfolgreich, aber 1 Datei(en) übersprungen: dokument_corrupt.pdf
  ✓ Removed 8 source PDF files
```

---

## Qualitätsstufen und Kompression

### High Quality (85% JPEG, 300 DPI)
- Beste Bildqualität
- 20-40% Reduktion
- Empfohlen für: Archivierung, wichtige Dokumente

### Medium Quality (75% JPEG, 200 DPI) - **Standard**
- Gute Balance zwischen Qualität und Größe
- 40-60% Reduktion
- Empfohlen für: Allgemeine Dokumente, E-Mail-Versand

### Low Quality (60% JPEG, 150 DPI)
- Maximale Kompression
- 60-80% Reduktion
- Empfohlen für: Große Archive, interne Dokumente
- ⚠️ Sichtbare JPEG-Artefakte bei Bildern möglich

### Original (Keine Kompression)
- Keine Änderung der Bildqualität
- Minimal-/keine Reduktion
- Empfohlen für: Wenn Originaldaten wichtig sind

---

## Probleme melden

Bei anhaltenden Problemen:

1. **Logdatei erstellen:** Speichern Sie den Processing Log
2. **Details sammeln:**
   - PDF-Dateiname und -größe
   - Vollständige Fehlermeldung
   - Quality-Einstellung
3. **GitHub Issue erstellen:** https://github.com/anthropics/claude-code/issues

---

## Tipps für beste Ergebnisse

✅ **DO:**
- Verwenden Sie "Medium Quality" für normale Dokumente
- Prüfen Sie das Ergebnis vor dem Löschen der Quelldateien
- Deaktivieren Sie "Remove source files" beim ersten Test

❌ **DON'T:**
- Verwenden Sie keine bereits stark komprimierten PDFs
- Verarbeiten Sie keine passwortgeschützten PDFs direkt
- Erwarten Sie keine Kompression bei reinen Text-PDFs

---

**Version:** 1.2.0
**Letzte Aktualisierung:** 2026-01-06
