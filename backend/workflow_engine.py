import time
import json
import requests
from typing import Dict, Any, List
from backend.database import db

class WorkflowEngine:
    """
    Automates business workflows:
    - Triggers approvals, compliance audits, and critical notifications based on extracted data
    - Evaluates custom business rules and thresholds
    - Dispatches downstream actions (webhooks, email alerts, ERP exports)
    """

    def __init__(self):
        self.webhook_urls: List[str] = []

    def evaluate_document_workflows(self, doc_id: int, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Runs all active workflow rules against newly extracted document data.
        Returns list of triggered events/alerts.
        """
        triggered_actions = []
        rules = db.get_workflow_rules()

        total_amount = float(structured_data.get("total_amount", 0.0) or 0.0)
        confidence_score = float(structured_data.get("confidence_score", 100.0) or 100.0)
        doc_type = structured_data.get("doc_type", "General")
        risk_assessment = structured_data.get("risk_assessment") or {}
        risk_level = risk_assessment.get("risk_level", "LOW")
        risk_flags = risk_assessment.get("flags", [])

        # Check line items sum vs total
        line_items = structured_data.get("line_items", [])
        line_sum = sum(float(item.get("total", 0.0) or 0.0) for item in line_items)
        subtotal = float(structured_data.get("subtotal", 0.0) or 0.0)
        tax = float(structured_data.get("tax_amount", 0.0) or 0.0)
        
        has_tax_discrepancy = False
        if line_items and line_sum > 0:
            expected_total = subtotal + tax if subtotal > 0 else line_sum
            if abs(expected_total - total_amount) > 5.0 and total_amount > 0:
                has_tax_discrepancy = True

        for rule in rules:
            if not rule.get("is_active"):
                continue

            rule_name = rule["rule_name"]
            threshold = float(rule.get("threshold_value") or 0.0)

            # Rule 1: High-Value Approval
            if rule_name == "High-Value Approval" and total_amount >= threshold:
                action = {
                    "rule_name": rule_name,
                    "event": f"High value transaction detected: {structured_data.get('currency', 'INR')} {total_amount:,.2f} >= ₹{threshold:,.0f}",
                    "action_taken": "Automated Routing to CFO Executive Approval Queue",
                    "severity": "CRITICAL",
                    "notes": f"High expenditure flagged for entity: {structured_data.get('entity_name', 'Unknown')}"
                }
                triggered_actions.append(action)
                db.log_workflow_alert(doc_id, action["rule_name"], action["event"], action["action_taken"], action["severity"], action["notes"])
                self._dispatch_webhook_simulation(doc_id, action)

            # Rule 2: Tax/Math Audit Flag
            elif rule_name == "Tax/Math Audit Flag" and (has_tax_discrepancy or "math" in " ".join(risk_flags).lower()):
                action = {
                    "rule_name": rule_name,
                    "event": f"Line items sum ({line_sum:,.2f}) + tax does not reconcile with stated total ({total_amount:,.2f})",
                    "action_taken": "Triggered Automated Tax Compliance Audit Flag",
                    "severity": "HIGH",
                    "notes": "Line item verification discrepancy flagged for finance review."
                }
                triggered_actions.append(action)
                db.log_workflow_alert(doc_id, action["rule_name"], action["event"], action["action_taken"], action["severity"], action["notes"])

            # Rule 3: Low Confidence Review
            elif rule_name == "Low Confidence Review" and confidence_score < threshold:
                action = {
                    "rule_name": rule_name,
                    "event": f"Extraction confidence {confidence_score:.1f}% is below quality threshold {threshold:.1f}%",
                    "action_taken": "Document flagged for Human-in-the-Loop manual verification",
                    "severity": "MEDIUM",
                    "notes": "Low confidence parsing detected. Please inspect extracted schema fields."
                }
                triggered_actions.append(action)
                db.log_workflow_alert(doc_id, action["rule_name"], action["event"], action["action_taken"], action["severity"], action["notes"])

            # Rule 4: Urgent Payment Due
            elif rule_name == "Urgent Payment Due":
                due_date_str = structured_data.get("due_date")
                if due_date_str and due_date_str != "N/A":
                    # Check urgency
                    action = {
                        "rule_name": rule_name,
                        "event": f"Invoice due date scheduled for {due_date_str}",
                        "action_taken": "Generated AP Urgent Payment Notification & Calendar Reminder",
                        "severity": "HIGH",
                        "notes": "Pending payment deadline alert."
                    }
                    triggered_actions.append(action)
                    db.log_workflow_alert(doc_id, action["rule_name"], action["event"], action["action_taken"], action["severity"], action["notes"])

            # Rule 5: Critical Health Biomarker
            elif rule_name == "Critical Health Biomarker" and doc_type == "Medical Report" and risk_level == "HIGH":
                action = {
                    "rule_name": rule_name,
                    "event": f"Abnormal clinical biomarker detected: {', '.join(risk_flags) if risk_flags else 'Elevated lab parameters'}",
                    "action_taken": "Dispatched Urgent Critical Care Alert to Attending Physician",
                    "severity": "CRITICAL",
                    "notes": f"Patient report requires immediate clinical review. Entity: {structured_data.get('entity_name')}"
                }
                triggered_actions.append(action)
                db.log_workflow_alert(doc_id, action["rule_name"], action["event"], action["action_taken"], action["severity"], action["notes"])
                self._dispatch_webhook_simulation(doc_id, action)

        return triggered_actions

    def _dispatch_webhook_simulation(self, doc_id: int, action: Dict[str, Any]):
        """
        Simulates external webhook notification dispatch (e.g. to Slack, ERP, Zapier, Webhook URLs).
        """
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": "DOCUMENT_INTELLIGENCE_TRIGGER",
            "document_id": doc_id,
            "rule": action.get("rule_name"),
            "severity": action.get("severity"),
            "action": action.get("action_taken"),
            "details": action.get("notes")
        }
        print(f"[Workflow Webhook Simulated] Dispatched event to ERP/Slack: {json.dumps(payload)}")

workflow_engine = WorkflowEngine()
