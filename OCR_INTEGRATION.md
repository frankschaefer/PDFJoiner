# OCR-Integration für LLM-Zugriff auf PDF-Text

## Übersicht

Um einem LLM (wie Claude) Zugriff auf Text aus gescannten PDFs zu geben, muss der Text **als durchsuchbarer Text** im PDF eingebettet sein. Dies erfordert OCR (Optical Character Recognition).

---

## Methoden zur OCR-Integration

### **Methode 1: OCRmyPDF (Empfohlen) ✅**

**OCRmyPDF** ist die beste Lösung - es fügt eine unsichtbare Textebene unter den Bildern ein.

#### Installation:
```bash
# macOS
brew install ocrmypdf
brew install tesseract-lang  # Für Deutsch

# Linux
sudo apt-get install ocrmypdf tesseract-ocr-deu

# Python-Integration
pip install ocrmypdf
```

#### Verwendung als Command-Line:
```bash
# Einfache OCR
ocrmypdf input.pdf output.pdf

# Mit Deutsch
ocrmypdf -l deu input.pdf output.pdf

# Mit Kompression
ocrmypdf -l deu --optimize 2 --jpeg-quality 75 input.pdf output.pdf

# Batch-Verarbeitung
for f in *.pdf; do
    ocrmypdf -l deu "$f" "ocr_$f"
done
```

#### Python-Integration:
```python
import ocrmypdf

def add_ocr_to_pdf(input_path: str, output_path: str, language: str = "deu"):
    """
    Fügt OCR-Textebene zu PDF hinzu.

    Args:
        input_path: Eingabe-PDF
        output_path: Ausgabe-PDF mit OCR
        language: Tesseract-Sprachcode (deu, eng, fra, etc.)
    """
    try:
        ocrmypdf.ocr(
            input_path,
            output_path,
            language=language,
            optimize=2,  # Bildoptimierung
            jpeg_quality=75,  # JPEG-Qualität
            skip_text=True,  # Überspringe Seiten mit Text
            force_ocr=False,  # Nicht bereits erkannten Text überschreiben
            deskew=True,  # Rotationskorrektur
            clean=True,  # Bildbereinigung
        )
        return True, ""
    except Exception as e:
        return False, str(e)
```

#### Vorteile:
- ✅ Unsichtbare Textebene (Originalbild bleibt sichtbar)
- ✅ Durchsuchbar für LLMs
- ✅ Automatische Spracherkennung
- ✅ Integrierte Bildoptimierung
- ✅ Überspringt bereits erkannte Seiten

---

### **Methode 2: Tesseract + pikepdf**

Manuelle Integration mit mehr Kontrolle.

```python
import pikepdf
from PIL import Image
import pytesseract
import io

def add_ocr_layer_to_page(pdf: pikepdf.Pdf, page_num: int, language: str = "deu"):
    """
    Fügt OCR-Textebene zu einer PDF-Seite hinzu.

    Args:
        pdf: pikepdf.Pdf Objekt
        page_num: Seitennummer (0-basiert)
        language: Tesseract-Sprache
    """
    page = pdf.pages[page_num]

    # Extrahiere Bilder von der Seite
    for image_key in page.images.keys():
        raw_image = page.images[image_key]
        pil_image = raw_image.as_pil_image()

        # OCR durchführen
        ocr_data = pytesseract.image_to_pdf_or_hocr(
            pil_image,
            lang=language,
            extension='pdf'
        )

        # TODO: OCR-Ergebnis in PDF-Page integrieren
        # Dies ist komplex und erfordert tiefes PDF-Verständnis

    return page
```

**Hinweis:** Diese Methode ist komplex und OCRmyPDF ist besser geeignet.

---

### **Methode 3: Integration in PDF-Joiner**

Fügen Sie OCR als optionalen Schritt nach dem Merge hinzu:

```python
# In batch_processor.py:

def process_folders(self, ..., enable_ocr: bool = False, ocr_language: str = "deu"):
    """
    ...
    Args:
        ...
        enable_ocr: OCR nach dem Merge durchführen
        ocr_language: OCR-Sprache
    """

    # ... existing merge code ...

    if success and enable_ocr:
        self._log(f"  ⏳ Running OCR on merged PDF...")

        # Temporärer Name
        temp_output = output_path + ".temp"

        try:
            import ocrmypdf
            ocrmypdf.ocr(
                output_path,
                temp_output,
                language=ocr_language,
                optimize=2,
                skip_text=True,
                force_ocr=False
            )

            # Ersetze Original mit OCR-Version
            import os
            os.replace(temp_output, output_path)

            self._log(f"  ✓ OCR completed successfully")
        except Exception as e:
            self._log(f"  ⚠ OCR failed: {str(e)}")
            # Fallback: behalte Original ohne OCR
```

**GUI-Integration:**

```python
# In batch_gui.py:

# Checkbox für OCR
self.ocr_var = ctk.BooleanVar(value=False)
self.ocr_checkbox = ctk.CTkCheckBox(
    options_frame,
    text="Add OCR text layer (macht PDFs durchsuchbar für LLMs)",
    variable=self.ocr_var,
    font=ctk.CTkFont(size=12)
)
self.ocr_checkbox.grid(row=2, column=0, padx=0, pady=(0, 5), sticky="w")

# OCR-Sprache auswählen
self.ocr_language_var = ctk.StringVar(value="deu")
ocr_lang_menu = ctk.CTkOptionMenu(
    options_frame,
    variable=self.ocr_language_var,
    values=["deu", "eng", "fra", "ita", "spa"],
    width=120
)
ocr_lang_menu.grid(row=2, column=1, padx=10, sticky="w")
```

---

## Wie LLMs auf OCR-Text zugreifen

### **1. Claude (Anthropic)**

Claude kann direkt PDFs mit OCR-Textebene lesen:

```python
import anthropic

# PDF hochladen
with open("document_with_ocr.pdf", "rb") as f:
    pdf_data = f.read()

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data.decode('latin1')  # oder base64.b64encode(pdf_data).decode()
                    }
                },
                {
                    "type": "text",
                    "text": "Fasse dieses Dokument zusammen."
                }
            ]
        }
    ]
)

print(message.content)
```

### **2. Text-Extraktion für andere LLMs**

Falls das LLM keine PDFs unterstützt:

```python
import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrahiert Text aus PDF mit OCR-Ebene.
    """
    text = ""

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"

    return text

# Verwenden mit LLM
pdf_text = extract_text_from_pdf("document_with_ocr.pdf")

# An LLM senden
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": f"Fasse diesen Text zusammen:\n\n{pdf_text}"}
    ]
)
```

---

## Qualität der OCR-Erkennung

### **Faktoren für gute OCR-Qualität:**

1. **Bildqualität:**
   - ✅ Mindestens 300 DPI
   - ✅ Klare, kontrastreiche Scans
   - ❌ Niedriger als 150 DPI → schlechte Erkennung

2. **Sprache:**
   - Richtige Tesseract-Sprachdaten installieren
   - Mehrsprachige Dokumente: `ocrmypdf -l deu+eng`

3. **Layout:**
   - ✅ Klares Layout, gerade Zeilen
   - ❌ Handschrift → sehr schlechte Erkennung
   - ❌ Komplexe Tabellen → teilweise problematisch

### **OCR-Genauigkeit testen:**

```bash
# OCR durchführen und Text extrahieren
ocrmypdf input.pdf output.pdf
pdftotext output.pdf output.txt

# Text prüfen
cat output.txt
```

---

## Empfohlener Workflow

### **Für PDF-Joiner Integration:**

1. **Merge PDFs** mit pikepdf (mit Kompression)
2. **OCR hinzufügen** mit OCRmyPDF (optional)
3. **Ergebnis prüfen** mit pdftotext

### **Beispiel-Code für kompletten Workflow:**

```python
def merge_and_ocr(
    pdf_files: List[str],
    output_path: str,
    quality: str = "medium",
    enable_ocr: bool = True,
    ocr_language: str = "deu"
) -> Tuple[bool, str]:
    """
    Merge PDFs mit Kompression und optionalem OCR.
    """
    # 1. Merge mit Kompression
    merger = PikePDFMerger(quality=quality)
    success, error = merger.merge_pdfs(pdf_files, output_path)
    merger.close()

    if not success:
        return False, error

    # 2. OCR hinzufügen (optional)
    if enable_ocr:
        temp_path = output_path + ".temp"

        try:
            import ocrmypdf
            ocrmypdf.ocr(
                output_path,
                temp_path,
                language=ocr_language,
                optimize=2,
                jpeg_quality=75,
                skip_text=True,
                deskew=True
            )

            # Ersetze Original
            import os
            os.replace(temp_path, output_path)

            return True, ""

        except Exception as e:
            # Fallback: behalte merged PDF ohne OCR
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return True, f"OCR failed: {str(e)}"

    return True, ""
```

---

## Alternative: Cloud-OCR-Services

Falls lokale OCR nicht ausreicht:

### **Google Cloud Vision API:**
```python
from google.cloud import vision

def ocr_with_google_vision(pdf_path: str):
    client = vision.ImageAnnotatorClient()

    with open(pdf_path, 'rb') as f:
        content = f.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    return response.full_text_annotation.text
```

### **Amazon Textract:**
```python
import boto3

def ocr_with_textract(pdf_path: str):
    textract = boto3.client('textract')

    with open(pdf_path, 'rb') as f:
        response = textract.analyze_document(
            Document={'Bytes': f.read()},
            FeatureTypes=['TABLES', 'FORMS']
        )

    return response
```

---

## Zusammenfassung

### **Beste Lösung für PDF-Joiner:**

1. ✅ **Installation:** `brew install ocrmypdf tesseract-lang`
2. ✅ **Integration:** Optional checkbox in GUI
3. ✅ **Workflow:** Merge → Compress → OCR
4. ✅ **LLM-Zugriff:** Claude kann PDFs direkt lesen

### **Quality Settings mit OCR:**

- **high** + OCR: Beste Qualität, langsam, große Dateien
- **medium** + OCR: Empfohlen - gute Balance
- **low** + OCR: Kleine Dateien, aber OCR-Qualität leidet
- **ultra-low** + OCR: ⚠️ Nicht empfohlen - OCR wird unzuverlässig

---

**Version:** 1.3.0
**Letzte Aktualisierung:** 2026-01-06

---

## ✅ Implementation Status

OCR-Integration ist jetzt **vollständig implementiert** in Version 1.3.0!

### Was wurde implementiert:

1. ✅ **OCRProcessor-Klasse** (`src/pdf_joiner/ocr_processor.py`)
   - Wrapper für OCRmyPDF-Kommandos
   - Batch-Verarbeitung mehrerer PDFs
   - Fehlerbehandlung und Timeout-Management
   - Unterstützung für alle Tesseract-Sprachen

2. ✅ **GUI-Integration** (`src/pdf_joiner/batch_gui.py`)
   - Checkbox: "🔍 Add OCR text layer (macht PDFs durchsuchbar für LLMs)"
   - Sprachauswahl: Deutsch, Englisch, Französisch, Italienisch, Spanisch, Portugiesisch, Niederländisch
   - Dynamische Beschreibungen und Statusanzeigen

3. ✅ **Optimaler Workflow** (implementiert in `batch_processor.py`)
   ```
   1. OCR auf einzelne PDFs (mit --skip-text für bereits erkannte Seiten)
   2. Bildkompression mit pikepdf (Quality-Einstellung)
   3. Zusammenführen aller PDFs
   ```

4. ✅ **Features:**
   - OCR nur auf Seiten ohne Text (`--skip-text`)
   - Inplace-Verarbeitung (ersetzt Original mit OCR-Version)
   - Parallele Verarbeitung mehrerer Dateien
   - Automatisches Überspringen bei Fehlern
   - Detaillierte Fehlerberichte

### Installation:

```bash
# macOS
brew install ocrmypdf tesseract-lang

# Linux
sudo apt-get install ocrmypdf tesseract-ocr-deu

# Windows
# Siehe: https://ocrmypdf.readthedocs.io/en/latest/installation.html
```

### Verwendung:

1. Starte PDF-Joiner: `./start.sh` oder `python main.py`
2. Aktiviere Checkbox: "🔍 Add OCR text layer"
3. Wähle Sprache aus Dropdown (Standard: Deutsch)
4. Wähle Quality-Einstellung (empfohlen: Medium oder Low für OCR)
5. Starte Verarbeitung

**Hinweis:** OCR wird nur durchgeführt, wenn OCRmyPDF installiert ist. Falls nicht verfügbar, wird eine Warnung angezeigt und die Verarbeitung ohne OCR fortgesetzt.

---
