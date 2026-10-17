import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from backend.config import DB_PATH

class Database:
    """Unified SQLite repository for queryable document intelligence datasets & workflow state."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Documents Table (Unified queryable schema)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT,
                doc_type TEXT DEFAULT 'General',
                title TEXT,
                document_number TEXT,
                entity_name TEXT,
                recipient_name TEXT,
                entity_address TEXT,
                gstin_tax_id TEXT,
                date TEXT,
                due_date TEXT,
                currency TEXT DEFAULT 'INR',
                subtotal REAL DEFAULT 0.0,
                tax_amount REAL DEFAULT 0.0,
                total_amount REAL DEFAULT 0.0,
                payment_status TEXT DEFAULT 'Pending Approval',
                department TEXT DEFAULT 'Finance',
                confidence_score REAL DEFAULT 90.0,
                detected_language TEXT DEFAULT 'English',
                risk_level TEXT DEFAULT 'LOW',
                risk_flags TEXT DEFAULT '[]',
                key_attributes TEXT DEFAULT '{}',
                summary TEXT,
                raw_text TEXT,
                structured_json TEXT,
                workflow_status TEXT DEFAULT 'PENDING_APPROVAL',
                approved_by TEXT,
                approved_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Line Items Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS line_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                item_id INTEGER,
                description TEXT,
                quantity REAL DEFAULT 1.0,
                unit_price REAL DEFAULT 0.0,
                total REAL DEFAULT 0.0,
                hsn_sac TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """)

            # Workflow Rules Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE,
                description TEXT,
                trigger_condition TEXT,
                threshold_value REAL,
                action_type TEXT,
                severity TEXT DEFAULT 'MEDIUM',
                is_active INTEGER DEFAULT 1
            )
            """)

            # Workflow Logs / Alerts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                rule_name TEXT,
                trigger_event TEXT,
                action_taken TEXT,
                severity TEXT DEFAULT 'INFO',
                status TEXT DEFAULT 'OPEN',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """)

            # Query History
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_query TEXT NOT NULL,
                ai_response TEXT,
                matched_doc_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Pre-populate default workflow rules if empty
            cursor.execute("SELECT COUNT(*) FROM workflow_rules")
            if cursor.fetchone()[0] == 0:
                default_rules = [
                    (
                        "High-Value Approval",
                        "Invoices exceeding ₹1,00,000 require CFO / VP Executive Approval",
                        "total_amount > 100000",
                        100000.0,
                        "ESCALATE_APPROVAL",
                        "CRITICAL",
                        1
                    ),
                    (
                        "Tax/Math Audit Flag",
                        "Discrepancy detected between line items sum and invoice total",
                        "tax_discrepancy == True",
                        0.0,
                        "TRIGGER_AUDIT_ALERT",
                        "HIGH",
                        1
                    ),
                    (
                        "Low Confidence Review",
                        "Extraction confidence below 85% requires Human-in-the-Loop verification",
                        "confidence_score < 85",
                        85.0,
                        "FLAG_FOR_REVIEW",
                        "MEDIUM",
                        1
                    ),
                    (
                        "Urgent Payment Due",
                        "Payment due in 5 days or already overdue",
                        "due_date_urgent == True",
                        5.0,
                        "DISPATCH_URGENT_ALERT",
                        "HIGH",
                        1
                    ),
                    (
                        "Critical Health Biomarker",
                        "Diagnostic report with abnormal biomarker readings",
                        "doc_type == 'Medical Report' and risk_level == 'HIGH'",
                        0.0,
                        "NOTIFY_PHYSICIAN",
                        "CRITICAL",
                        1
                    )
                ]
                cursor.executemany("""
                INSERT INTO workflow_rules (rule_name, description, trigger_condition, threshold_value, action_type, severity, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, default_rules)

            conn.commit()

    def insert_document(self, data: Dict[str, Any], raw_text: str = "", file_path: str = "") -> int:
        """Insert structured document and its line items into unified queryable dataset."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            risk_assessment = data.get("risk_assessment") or {}
            risk_level = risk_assessment.get("risk_level", "LOW")
            risk_flags = json.dumps(risk_assessment.get("flags", []))
            key_attrs = json.dumps(data.get("key_attributes", {}))
            structured_str = json.dumps(data)

            # Determine initial workflow status
            workflow_status = "PENDING_APPROVAL"
            if data.get("total_amount", 0) > 100000:
                workflow_status = "FLAGGED_HIGH_VALUE"
            elif risk_level == "HIGH":
                workflow_status = "FLAGGED_AUDIT"

            cursor.execute("""
            INSERT INTO documents (
                filename, file_path, doc_type, title, document_number, entity_name, recipient_name,
                entity_address, gstin_tax_id, date, due_date, currency, subtotal, tax_amount,
                total_amount, payment_status, department, confidence_score, detected_language,
                risk_level, risk_flags, key_attributes, summary, raw_text, structured_json,
                workflow_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("filename", data.get("title", "Document")),
                file_path,
                data.get("doc_type", "General"),
                data.get("title", "Extracted Document"),
                data.get("document_number", "N/A"),
                data.get("entity_name", "N/A"),
                data.get("recipient_name", "N/A"),
                data.get("entity_address", "N/A"),
                data.get("gstin_tax_id", "N/A"),
                data.get("date", time.strftime("%Y-%m-%d")),
                data.get("due_date", "N/A"),
                data.get("currency", "INR"),
                float(data.get("subtotal", 0.0) or 0.0),
                float(data.get("tax_amount", 0.0) or 0.0),
                float(data.get("total_amount", 0.0) or 0.0),
                data.get("payment_status", "Pending Approval"),
                data.get("department", "Finance"),
                float(data.get("confidence_score", 90.0) or 90.0),
                data.get("detected_language", "English"),
                risk_level,
                risk_flags,
                key_attrs,
                data.get("summary", ""),
                raw_text,
                structured_str,
                workflow_status
            ))

            doc_id = cursor.lastrowid

            # Insert line items
            line_items = data.get("line_items", [])
            for item in line_items:
                cursor.execute("""
                INSERT INTO line_items (document_id, item_id, description, quantity, unit_price, total, hsn_sac)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    item.get("item_id", 1),
                    item.get("description", "Item"),
                    float(item.get("quantity", 1.0) or 1.0),
                    float(item.get("unit_price", 0.0) or 0.0),
                    float(item.get("total", 0.0) or 0.0),
                    item.get("hsn_sac", "N/A")
                ))

            conn.commit()
            return doc_id

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            doc = dict(row)
            doc["risk_flags"] = json.loads(doc.get("risk_flags") or "[]")
            doc["key_attributes"] = json.loads(doc.get("key_attributes") or "{}")
            
            # Fetch line items
            cursor.execute("SELECT * FROM line_items WHERE document_id = ?", (doc_id,))
            doc["line_items"] = [dict(r) for r in cursor.fetchall()]
            
            # Fetch workflow logs
            cursor.execute("SELECT * FROM workflow_logs WHERE document_id = ? ORDER BY id DESC", (doc_id,))
            doc["workflow_logs"] = [dict(r) for r in cursor.fetchall()]

            return doc

    def list_documents(self, doc_type: str = None, department: str = None, status: str = None, search: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM documents WHERE 1=1"
        params = []

        if doc_type:
            query += " AND doc_type = ?"
            params.append(doc_type)
        if department:
            query += " AND department = ?"
            params.append(department)
        if status:
            query += " AND (workflow_status = ? OR payment_status = ?)"
            params.extend([status, status])
        if search:
            query += " AND (title LIKE ? OR entity_name LIKE ? OR document_number LIKE ? OR gstin_tax_id LIKE ?)"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            docs = []
            for r in rows:
                d = dict(r)
                d["risk_flags"] = json.loads(d.get("risk_flags") or "[]")
                docs.append(d)
            return docs

    def update_document_workflow(self, doc_id: int, status: str, approved_by: str = "Admin", notes: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE documents
            SET workflow_status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (status, approved_by, doc_id))

            # Log workflow event
            cursor.execute("""
            INSERT INTO workflow_logs (document_id, rule_name, trigger_event, action_taken, severity, status, notes)
            VALUES (?, 'Manual Workflow Action', ?, ?, 'INFO', 'RESOLVED', ?)
            """, (doc_id, f"Document marked as {status}", f"Action executed by {approved_by}", notes))

            conn.commit()

    def update_document_data(self, doc_id: int, updated_fields: Dict[str, Any]):
        """Allows Human-in-the-Loop editing of extracted fields."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            allowed = [
                "title", "entity_name", "document_number", "gstin_tax_id",
                "subtotal", "tax_amount", "total_amount", "date", "due_date",
                "payment_status", "department", "confidence_score"
            ]
            for k, v in updated_fields.items():
                if k in allowed:
                    fields.append(f"{k} = ?")
                    values.append(v)

            if fields:
                values.append(doc_id)
                query = f"UPDATE documents SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()

    def log_workflow_alert(self, doc_id: int, rule_name: str, trigger_event: str, action_taken: str, severity: str = "MEDIUM", notes: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO workflow_logs (document_id, rule_name, trigger_event, action_taken, severity, status, notes)
            VALUES (?, ?, ?, ?, ?, 'OPEN', ?)
            """, (doc_id, rule_name, trigger_event, action_taken, severity, notes))
            conn.commit()

    def get_workflow_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT l.*, d.title as doc_title, d.entity_name, d.total_amount, d.currency
            FROM workflow_logs l
            LEFT JOIN documents d ON l.document_id = d.id
            ORDER BY l.id DESC LIMIT ?
            """, (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_workflow_rules(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflow_rules ORDER BY id ASC")
            return [dict(r) for r in cursor.fetchall()]

    def toggle_rule(self, rule_id: int, is_active: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE workflow_rules SET is_active = ? WHERE id = ?", (1 if is_active else 0, rule_id))
            conn.commit()

    def record_query(self, user_query: str, ai_response: str, matched_doc_ids: List[int]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO query_history (user_query, ai_response, matched_doc_ids)
            VALUES (?, ?, ?)
            """, (user_query, ai_response, json.dumps(matched_doc_ids)))
            conn.commit()

    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM query_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            out = []
            for r in rows:
                item = dict(r)
                item["matched_doc_ids"] = json.loads(item.get("matched_doc_ids") or "[]")
                out.append(item)
            return out

db = Database()
