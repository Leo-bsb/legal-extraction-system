## 📄 Legal Document Information Extraction System (LLM + Streamlit + RAG)

A full-stack, production-oriented **legal information extraction platform** built with **Streamlit**, a modular backend for PDF processing, and **Gemini 2.5 Flash** for LLM-based extraction.
The system supports **single-document extraction**, **batch processing**, **dashboard visualization**, and **SQLite persistence** — with a clean UI suitable for real-world use.

---

## 🚀 Key Features

### 🔍 **1. Single Document Extraction**

* Upload a PDF (up to 200MB).
* Extract structured information using:

  * Text parsing
  * OCR fallback
  * Metadata cleanup
  * Gemini 2.5 Flash reasoning model
* Validate, preview and download results.

### 📦 **2. Batch Processing**

* Upload multiple PDFs.
* Parallel processing with status display.
* Download batch results as JSON or CSV.

### 📊 **3. Dashboard**

* Visualize previous extractions.
* Filter by date, type and extracted entities.
* Monitor processing history and trends.

### 🗄️ **4. Database Integration**

* SQLite storage for:

  * Document metadata
  * Extracted fields
  * Processing timestamps and errors
* Automatic ID generation and indexing.

### 🎨 **5. Professional Streamlit UI**

* Custom CSS (dark/light hybrid).
* Responsive layout.
* Progress feedback and error handling.
* Modular page architecture.

---

## 🧠 Architecture Overview

```
streamlit_app.py         # Main UI / routing
│
├── data_validator/      # Schema validation & cleaning
├── dashboard/           # Charts, summaries, historical analytics
├── db/                  # SQLite connection + CRUD
├── interfaces/          # DTOs, standard structures
├── llm_engine/          # Gemini 2.5 Flash integration + prompting
├── pdf_processor/       # Text extraction, OCR, heuristics
└── utils/               # Logging, file ops, helpers
```

### LLM Layer (Gemini 2.5 Flash)

* Structured prompting
* Temperature/stability settings optimized for legal text
* Output schema checks and fallback repairs
* Configurable extraction recipes

### PDF Processor Layer

* Robust text extraction pipeline
* Automatic encoding normalization
* Split + clean + merge strategy
* OCR fallback for scanned documents

### Storage Layer

* SQLite (local) with Indexed tables
* Insert/update abstraction
* Query helpers for dashboards

---

## 🧪 Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend UI   | Streamlit                        |
| LLM           | **Gemini 2.5 Flash**             |
| Data Storage  | SQLite                           |
| PDF Parsing   | PyPDF + OCR                      |
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

Create `.env`:

```
GEMINI_API_KEY=your_key_here
```

### 4. Run the app:

```bash
streamlit run streamlit_app.py
```

---

## 🧠 How Extraction Works (High-Level)

1. User uploads a PDF
2. PDF is processed → text extracted + cleaned
3. A structured prompt is generated
4. **Gemini 2.5 Flash** receives the prompt and returns a JSON result
5. Schema validator cleans fields
6. Result + metadata is stored in SQLite
7. UI renders preview + download options

Each step is fully modular and can be swapped or extended.

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

This project was built to demonstrate:

* Real-world legal document extraction
* Clean architecture for LLM systems
* Practical integration of **Gemini 2.5 Flash**
* UI/UX suitable for production
* Modular extensibility (cloud DBs, new schemas, RAG layers)

It can evolve into:

* A full document intelligence platform
* A corporate data ingestion pipeline
* A SaaS product for legal firms
