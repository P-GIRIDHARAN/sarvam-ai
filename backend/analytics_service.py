import io
import csv
import json
from typing import Dict, Any, List
from backend.database import db

class AnalyticsService:
    """
    Transforms unstructured document data into analytics-ready formats
    for BI dashboards, executive reporting, and data export.
    """

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Calculates executive KPI cards and dynamic chart datasets."""
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Total docs & financial volume
            cursor.execute("""
            SELECT 
                COUNT(*) as total_docs,
                COALESCE(SUM(total_amount), 0.0) as total_volume,
                COALESCE(AVG(confidence_score), 0.0) as avg_confidence
            FROM documents
            """)
            overall = dict(cursor.fetchone())

            # Pending approvals & flags
            cursor.execute("""
            SELECT 
                COUNT(CASE WHEN workflow_status LIKE '%PENDING%' OR workflow_status LIKE '%FLAGGED%' THEN 1 END) as pending_actions,
                COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high_risk_count
            FROM documents
            """)
            status_counts = dict(cursor.fetchone())

            # Document Type Distribution (for Donut Chart)
            cursor.execute("""
            SELECT doc_type, COUNT(*) as count, COALESCE(SUM(total_amount), 0.0) as total_val
            FROM documents
            GROUP BY doc_type
            ORDER BY count DESC
            """)
            type_distribution = [dict(r) for r in cursor.fetchall()]

            # Top Vendors / Entities by Spend
            cursor.execute("""
            SELECT entity_name, COUNT(*) as doc_count, COALESCE(SUM(total_amount), 0.0) as spend
            FROM documents
            WHERE entity_name IS NOT NULL AND entity_name != 'N/A' AND entity_name != ''
            GROUP BY entity_name
            ORDER BY spend DESC
            LIMIT 6
            """)
            top_vendors = [dict(r) for r in cursor.fetchall()]

            # Language Distribution (leveraging Sarvam AI's Indic capability)
            cursor.execute("""
            SELECT detected_language, COUNT(*) as count, AVG(confidence_score) as avg_conf
            FROM documents
            GROUP BY detected_language
            ORDER BY count DESC
            """)
            language_split = [dict(r) for r in cursor.fetchall()]

            # Workflow Pipeline Status
            cursor.execute("""
            SELECT workflow_status, COUNT(*) as count
            FROM documents
            GROUP BY workflow_status
            """)
            workflow_pipeline = [dict(r) for r in cursor.fetchall()]

            # Recent Alerts Feed
            cursor.execute("""
            SELECT l.*, d.title as doc_title, d.entity_name
            FROM workflow_logs l
            LEFT JOIN documents d ON l.document_id = d.id
            ORDER BY l.id DESC
            LIMIT 5
            """)
            recent_alerts = [dict(r) for r in cursor.fetchall()]

            return {
                "kpis": {
                    "total_documents": overall["total_docs"],
                    "total_financial_volume": round(overall["total_volume"], 2),
                    "avg_confidence_score": round(overall["avg_confidence"], 1),
                    "pending_actions": status_counts["pending_actions"],
                    "high_risk_alerts": status_counts["high_risk_count"],
                    "avg_processing_speed": "1.2s / doc"
                },
                "type_distribution": type_distribution,
                "top_vendors": top_vendors,
                "language_split": language_split,
                "workflow_pipeline": workflow_pipeline,
                "recent_alerts": recent_alerts
            }

    @staticmethod
    def export_dataset_csv() -> str:
        """Exports unified queryable dataset into analytics-ready CSV format for BI tools."""
        docs = db.list_documents(limit=5000)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "Document ID",
            "Document Type",
            "Title",
            "Document Number",
            "Entity / Vendor",
            "Recipient",
            "GSTIN / Tax ID",
            "Issue Date",
            "Due Date",
            "Currency",
            "Subtotal",
            "Tax Amount",
            "Total Amount",
            "Payment Status",
            "Department",
            "Extraction Confidence (%)",
            "Language",
            "Risk Level",
            "Workflow Status",
            "Approved By",
            "Created At"
        ])

        for d in docs:
            writer.writerow([
                d.get("id"),
                d.get("doc_type"),
                d.get("title"),
                d.get("document_number"),
                d.get("entity_name"),
                d.get("recipient_name"),
                d.get("gstin_tax_id"),
                d.get("date"),
                d.get("due_date"),
                d.get("currency"),
                d.get("subtotal"),
                d.get("tax_amount"),
                d.get("total_amount"),
                d.get("payment_status"),
                d.get("department"),
                d.get("confidence_score"),
                d.get("detected_language"),
                d.get("risk_level"),
                d.get("workflow_status"),
                d.get("approved_by") or "N/A",
                d.get("created_at")
            ])

        return output.getvalue()

    @staticmethod
    def export_dataset_json() -> List[Dict[str, Any]]:
        """Exports unified dataset as structured JSON."""
        return db.list_documents(limit=5000)

analytics_service = AnalyticsService()
