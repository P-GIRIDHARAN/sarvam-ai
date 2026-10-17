import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse

from backend.config import UPLOAD_DIR, SAMPLES_DIR, ROOT_DIR, SARVAM_API_KEY
from backend.sarvam_client import sarvam_client
from backend.document_parser import document_parser
from backend.database import db
from backend.workflow_engine import workflow_engine
from backend.analytics_service import analytics_service
from backend.sample_data import load_sample_documents_into_system, SAMPLE_DOCUMENTS

app = FastAPI(
    title="DocuPulse AI - Document Intelligence Agent",
    description="Intelligent Multimodal Document Intelligence Platform powered by Sarvam AI",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Populate samples on initial boot if empty
try:
    load_sample_documents_into_system()
except Exception as e:
    print(f"[Sample Init Warning]: {e}")

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    """Verify backend and Sarvam AI API connectivity."""
    sarvam_status = sarvam_client.test_connection()
    return {
        "status": "online",
        "sarvam_ai": sarvam_status,
        "database": "sqlite3_ready",
        "api_key_masked": f"{sarvam_client.api_key[:8]}...{sarvam_client.api_key[-4:]}" if sarvam_client.api_key else "None"
    }

@app.post("/api/settings/sarvam")
def update_sarvam_settings(data: Dict[str, str]):
    """Update Sarvam AI API Key dynamically."""
    new_key = data.get("api_key", "").strip()
    if not new_key:
        raise HTTPException(status_code=400, detail="API key is required.")
    
    sarvam_client.set_api_key(new_key)
    test_result = sarvam_client.test_connection()
    return {
        "success": test_result["status"] == "connected",
        "connection": test_result
    }

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_hint: Optional[str] = Form(None),
    language: Optional[str] = Form("en-IN")
):
    """
    Ingest & structure document:
    1. Save uploaded file to disk
    2. Extract raw text & tables
    3. Process with Sarvam AI (Doc-AI / Sarvam-105b)
    4. Index into Unified Queryable Dataset
    5. Evaluate Automated Business Workflows
    """
    safe_filename = file.filename.replace(" ", "_")
    target_path = UPLOAD_DIR / safe_filename
    
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 1: Extract text and layout
    raw_text, meta = document_parser.extract_text_from_file(str(target_path))

    # Step 2: Use Sarvam AI to structure the unstructured text
    structured = sarvam_client.extract_structured_data(raw_text, doc_hint=doc_hint)
    structured["filename"] = file.filename
    structured["file_size"] = meta.get("file_size")

    # Step 3: Insert into Unified Dataset
    doc_id = db.insert_document(structured, raw_text=raw_text, file_path=f"uploads/{safe_filename}")

    # Step 4: Run Workflow Automation Engine
    triggered_workflows = workflow_engine.evaluate_document_workflows(doc_id, structured)

    return {
        "success": True,
        "document_id": doc_id,
        "structured_data": structured,
        "metadata": meta,
        "triggered_workflows": triggered_workflows
    }

@app.post("/api/documents/load-samples")
def load_samples():
    """1-Click load realistic diverse sample documents into the system."""
    loaded_count = load_sample_documents_into_system()
    return {
        "success": True,
        "message": f"Sample documents synchronized successfully.",
        "count": loaded_count
    }

@app.get("/api/documents")
def list_documents(
    doc_type: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100
):
    """Retrieve filtered documents from the unified dataset."""
    docs = db.list_documents(doc_type=doc_type, department=department, status=status, search=search, limit=limit)
    return {"documents": docs, "total": len(docs)}

@app.get("/api/documents/{doc_id}")
def get_document_details(doc_id: int):
    """Get full document profile, schema attributes, line items, and audit trail."""
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@app.put("/api/documents/{doc_id}")
def update_document_fields(doc_id: int, fields: Dict[str, Any]):
    """Human-in-the-Loop editing of extracted fields."""
    db.update_document_data(doc_id, fields)
    return {"success": True, "updated": fields}

@app.post("/api/documents/{doc_id}/workflow")
def execute_workflow_action(doc_id: int, action_data: Dict[str, Any]):
    """Approve, Reject, or Escalate document in workflow pipeline."""
    status = action_data.get("status", "APPROVED")
    approved_by = action_data.get("approved_by", "Authorized Officer")
    notes = action_data.get("notes", "")
    
    db.update_document_workflow(doc_id, status=status, approved_by=approved_by, notes=notes)
    return {
        "success": True,
        "document_id": doc_id,
        "new_status": status,
        "approved_by": approved_by
    }

@app.post("/api/documents/{doc_id}/translate")
def translate_document(doc_id: int, data: Dict[str, str]):
    """Translate document summary into Indic languages using Sarvam translate endpoint."""
    target_lang = data.get("target_language", "hi-IN")
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    text_to_translate = doc.get("summary") or doc.get("title", "")
    translated = sarvam_client.translate(text_to_translate, source_lang="en-IN", target_lang=target_lang)
    return {
        "original": text_to_translate,
        "translated": translated,
        "target_language": target_lang
    }

@app.post("/api/query")
def query_agent(data: Dict[str, str]):
    """
    Unified Dataset Explorer: Natural Language Agent Q&A powered by Sarvam AI (sarvam-105b).
    """
    query = data.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Fetch context documents
    docs = db.list_documents(limit=50)
    agent_response = sarvam_client.answer_unified_query(query, docs)

    # Save to query history
    matched_ids = agent_response.get("matched_doc_ids", [])
    db.record_query(query, agent_response.get("answer", ""), matched_ids)

    # Fetch matched doc details for UI side panel
    matched_records = []
    for doc_id in matched_ids:
        doc = db.get_document(doc_id)
        if doc:
            matched_records.append(doc)

    return {
        "query": query,
        "answer": agent_response.get("answer"),
        "matched_documents": matched_records,
        "model": agent_response.get("model_used")
    }

@app.get("/api/query/history")
def get_query_history():
    return {"history": db.get_query_history()}

@app.get("/api/analytics/dashboard")
def get_analytics_dashboard():
    """Analytics KPIs and BI visualization aggregations."""
    return analytics_service.get_dashboard_metrics()

@app.get("/api/analytics/export/csv")
def export_csv():
    csv_data = analytics_service.export_dataset_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sarvam_document_dataset.csv"}
    )

@app.get("/api/analytics/export/json")
def export_json():
    json_data = analytics_service.export_dataset_json()
    return JSONResponse(content=json_data)

@app.get("/api/workflows/rules")
def get_rules():
    return {"rules": db.get_workflow_rules()}

@app.post("/api/workflows/rules/{rule_id}/toggle")
def toggle_rule(rule_id: int, data: Dict[str, bool]):
    db.toggle_rule(rule_id, data.get("is_active", True))
    return {"success": True, "rule_id": rule_id, "is_active": data.get("is_active", True)}

@app.get("/api/workflows/alerts")
def get_alerts():
    return {"alerts": db.get_workflow_alerts()}

# Serve uploaded & sample files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")

# Serve Frontend static assets
FRONTEND_DIR = ROOT_DIR / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return PlainTextResponse("Frontend build in progress...")
