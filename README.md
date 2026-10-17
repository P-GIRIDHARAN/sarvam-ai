# DocuPulse AI - Document Intelligence Agent
### Multimodal Document Extraction, Unified Datasets, Analytics Dashboards & Workflow Automation powered by Sarvam AI

![Sarvam AI](https://img.shields.io/badge/Powered%20By-Sarvam%20AI-6366f1)
![Model](https://img.shields.io/badge/Model-sarvam--105b-8b5cf6)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-10b981)
![Multilingual](https://img.shields.io/badge/Languages-English%20%2B%2022%20Indic%20Languages-06b6d4)

---

## 🌟 Core Pillars & Capabilities

### 1. Multimodal Document Extraction & Structuring
- **Multi-Format Ingestion**: Ingests PDFs, images, scans, invoices, purchase orders, tax/GST forms, medical/lab reports, utility bills, and commercial contracts.
- **Sarvam AI Intelligence**:
  - Full layout and table preservation using Sarvam Doc-AI & OCR.
  - Schema-driven extraction powered by flagship **`sarvam-105b`** reasoning models.
  - Normalization into strict, unified queryable entities: `doc_type`, `document_number`, `entity_name`, `gstin_tax_id`, `subtotal`, `tax_amount`, `total_amount`, `payment_status`, `confidence_score`, `line_items` (tables), `risk_flags`, and `key_attributes`.
- **Multilingual Indic Support**: Native understanding and translation across **22 constitutionally recognized Indian languages** (Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, etc.) plus English.

### 2. Unified Queryable Dataset & Natural Language RAG Agent
- **Grounded AI Synthesis**: Ask natural language questions in English or Indic languages:
  - *"What is our total invoice spend pending approval?"*
  - *"List all high-risk documents with tax discrepancies."*
  - *"Summarize clinical findings and elevated glucose levels in patient blood tests."*
  - *"Which vendors are registered in Maharashtra with GST?"*
- **Live Dataset Exploration**: Filters, searches, and exports structured records directly into BI-ready CSV or JSON.

### 3. Insights & Executive BI Dashboards
- **Executive KPIs**: Real-time tracking of Total Processed Volume (₹), Extraction Confidence (%), Pending Approvals, High-Risk Flags, and Turnaround Speed.
- **Financial Visualizations**: Vendor spend ranking, classification breakdown (Invoices vs. POs vs. Reports), and language distribution.
- **Anomaly Matrix**: Mismatched line items math, missing tax IDs, and overdue approval alerts.

### 4. Automated Business Workflows & Human-in-the-Loop
- **Rule Engine**:
  - 🚨 **High-Value Threshold**: Automatically escalates invoices > ₹1,00,000 to CFO/VP tier.
  - 🔍 **Tax & Math Discrepancy**: Audits line items sum vs. stated total and flags variances.
  - 🩺 **Critical Health Biomarkers**: Detects abnormal diagnostic readings and triggers physician alerts.
  - ⏳ **SLA Urgency Alerts**: Flags impending payment due dates (< 5 days).
  - 🎯 **Confidence Guardrails**: Flags documents with < 85% confidence for Human-in-the-Loop verification.
- **Side-by-Side Inspector Drawer**:
  - Live side-by-side verification of original text against extracted JSON schema.
  - Field-level editing before final sign-off.
  - 1-click Indic translation of document summaries.
  - Approval / Rejection decisions with full audit logging.

---

## 🚀 Quickstart Guide

### 1. Requirements & Dependencies
Make sure you have Python 3.10+ installed.

```bash
cd c:\Users\pgiri\Downloads\sarvam-ai
pip install -r requirements.txt
```

### 2. Configure Sarvam AI API Key
The API key is already configured in `.env`:
```env
SARVAM_API_KEY=sk_1yj1b7cl_r1dVNNBcBtb27ZNB00h1x1HL
SARVAM_BASE_URL=https://api.sarvam.ai
SARVAM_LLM_MODEL=sarvam-105b
PORT=8000
HOST=127.0.0.1
```
*(You can also update or test your key live from the UI Settings modal).*

### 3. Launch the Application
Run the startup script:
```bash
python run.py
```
Open your browser at:
```
http://127.0.0.1:8000
```

---

## 📂 Project Architecture

```
sarvam-ai/
├── backend/
│   ├── app.py                 # FastAPI REST API & Static Asset Server
│   ├── sarvam_client.py       # Sarvam AI API Wrapper (Sarvam-105b, Doc-AI, Translate)
│   ├── document_parser.py     # PDF & Multimodal layout extraction engine
│   ├── database.py            # SQLite Unified Queryable Dataset & Audit Logs
│   ├── workflow_engine.py     # Business Rules & Automated Triggers Engine
│   ├── analytics_service.py   # BI KPIs, Trends & CSV/JSON Exporters
│   ├── sample_data.py         # Realistic Multi-Industry Enterprise Datasets
│   ├── pdf_generator.py       # Physical PDF document generator for testing
│   └── config.py              # Environment & Configuration Settings
├── frontend/
│   ├── index.html             # Executive Single Page Web App
│   ├── css/
│   │   └── style.css          # Modern dark theme, glassmorphism & responsive styles
│   └── js/
│       └── app.js             # UI state orchestration, charts, drawer & RAG Q&A
├── samples/                   # Generated test PDFs (Invoices, Lab Reports, POs, Bills)
├── run.py                     # 1-Click Server Launch Script
├── requirements.txt           # Python dependencies
└── .env                       # Pre-configured Sarvam AI credentials
```

---

## ⚡ Built-in Enterprise Test Samples

Click **"⚡ Load Samples"** in the top bar to test the pipeline with pre-configured documents:
1. **Tata Consultancy Services Cloud Invoice**: High-value compute invoice (₹1,85,400) triggering CFO escalation.
2. **Apollo Diagnostics Metabolic Panel**: Clinical report with elevated Glucose & HbA1c triggering critical health alerts.
3. **Reliance Retail Purchase Order**: Commercial procurement PO for fulfillment hardware (₹4,45,000).
4. **BESCOM Karnataka Commercial Utility Bill**: Bilingual English + Kannada electricity bill (₹56,832.60).
5. **Infosys Master Services Licensing Contract**: Annual enterprise software licensing contract (₹14,16,000).

---

## 🛡️ License
Proprietary & Confidential - Built for Document Intelligence with Sarvam AI.
