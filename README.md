
<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/Streamlit-App-red" />
  <img src="https://img.shields.io/badge/Gemini-2.5_Flash-blue" />
</p>

## 📄 Legal Document Text Extraction System (LLM + Streamlit + PDF Processing)

**Try the live demo:** [https://huggingface.co/spaces/leo-bsb/legal-extraction-system](https://huggingface.co/spaces/leo-bsb/legal-extraction-system)

> ⚠️ **Note:** This app interface is currently available in Brazilian Portuguese only.


A full-stack, production-ready **legal document text extraction platform** built with **Streamlit**, a modular backend for robust PDF processing, and **Gemini 2.5 Flash** for LLM-enhanced structured data extraction.
The system supports **single-document and batch PDF text extraction**, **dashboard visualization**, and **SQLite-based storage**, all wrapped in a clean, user-friendly interface designed for practical use.

---

## 🚀 Key Features

### 🔍 **1. Single Document Text Extraction**

* Upload PDF files (up to 200MB).
* Extract text and structured information using:

  * Advanced PDF text parsing
  * OCR fallback for scanned or image-based PDFs
  * Metadata cleanup and normalization
  * Gemini 2.5 Flash reasoning and data extraction
* Preview, validate, and download extracted data.

### 📦 **2. Batch PDF Processing**

* Upload multiple PDFs simultaneously.
* Parallel extraction with real-time status updates.
* Download consolidated extraction results in JSON or CSV formats.

### 📊 **3. Extraction History Dashboard**

* Visualize and filter past extractions by date, document type, and extracted entities.
* Monitor extraction accuracy and processing trends over time.

### 🗄️ **4. Persistent Storage**

* SQLite database for storing:

  * Document metadata
  * Extracted text and structured fields
  * Processing timestamps and error logs
* Automatic indexing for efficient queries and dashboard updates.

### 🎨 **5. Professional Streamlit UI**

* Custom dark/light hybrid CSS theme.
* Responsive, intuitive layout with progress feedback.
* Modular page design for maintainability and extensibility.

---

## 🧠 Architecture Overview

```
streamlit_app.py         # Main UI and routing
│
├── pdf_processor/       # PDF text extraction and OCR pipeline
├── llm_engine/          # Gemini 2.5 Flash integration and prompting
├── data_validator/      # Schema validation and data cleaning
├── dashboard/           # Visualization and analytics components
├── db/                  # SQLite connection and CRUD operations
├── interfaces/          # Data transfer objects and standard formats
└── utils/               # Logging, file operations, helpers
```

### LLM Layer (Gemini 2.5 Flash)

* Structured prompting tailored for legal documents
* Temperature and stability tuning for consistent results
* Output schema validation and automatic error correction
* Customizable extraction templates

### PDF Processor Layer

* Robust text extraction handling various PDF encodings
* OCR fallback to ensure text extraction from scanned images
* Intelligent splitting, cleaning, and merging of content for LLM input

### Storage Layer

* Local SQLite database with indexed tables
* Insert/update abstractions for reliable persistence
* Query helpers for dashboard filtering and reporting

---

## 🧪 Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend UI   | Streamlit                        |
| LLM           | **Gemini 2.5 Flash**             |
| Data Storage  | SQLite                           |
| PDF Parsing   | PyPDF + OCR (Tesseract)          |
| Language      | Python                           |
| Visualization | Streamlit charts (Altair/Pandas) |

---

## ⚙️ Installation

### 1. Clone the repository:

```bash
git clone https://github.com/your-user/legal-llm-extractor.git
cd legal-llm-extractor
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Add your API key:

Create a `.env` file with:

```
GEMINI_API_KEY=your_key_here
```

### 4. Run the app:

```bash
streamlit run streamlit_app.py
```

---

## 🧠 How Extraction Works (Overview)

1. Upload a PDF document.
2. PDF Processor extracts raw text, applies OCR if necessary, and cleans the content.
3. Generate a structured prompt based on the cleaned text.
4. Gemini 2.5 Flash processes the prompt, extracting relevant structured data as JSON.
5. Validation layer cleans and normalizes extracted fields.
6. Results and metadata are stored in SQLite.
7. UI displays extraction preview with options to download or continue processing.

Each component is modular and can be customized or replaced independently.

---

## 📁 Output Examples

### JSON

```json
{
  "case_id": "0001234-56.2023.8.01.0001",
  "parties": ["Aman Semi Conductors", "Haryana State Indust Dev Corp"],
  "date": "2023-02-27",
  "summary": "Dispute regarding industrial land lease terms...",
  "extraction_confidence": 0.92
}
```

### CSV (Batch)

```
filename,case_id,date,parties,summary
doc1.pdf,0001234-56.2023...,2023-02-27,"Aman; Haryana",Dispute regarding...
```

---

## 🏗️ Project Goals & Vision

Designed to demonstrate:

* Reliable and scalable legal document text extraction
* Clean, maintainable architecture for combining PDF processing and LLMs
* Practical integration of Gemini 2.5 Flash with a professional UI
* Extensible foundation for advanced document intelligence workflows

Future directions include:

* Expanding support for additional document types
* Integration with cloud databases and storage
* Enhancing extraction models and adding annotation interfaces
* Developing SaaS solutions tailored to legal and corporate clients
