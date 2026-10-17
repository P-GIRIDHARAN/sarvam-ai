import os
import json
from pathlib import Path
from backend.config import SAMPLES_DIR
from backend.database import db
from backend.workflow_engine import workflow_engine

SAMPLE_DOCUMENTS = [
    {
        "filename": "TCS_Cloud_Infrastructure_Invoice_2026.pdf",
        "doc_type": "Invoice",
        "title": "Tata Consultancy Services - Cloud & Enterprise AI Infrastructure Invoice",
        "document_number": "TCS-IN-2026-9842",
        "entity_name": "Tata Consultancy Services Ltd",
        "recipient_name": "Sarvam AI Technologies Pvt Ltd",
        "entity_address": "TCS House, Raveline Street, Fort, Mumbai, Maharashtra 400001",
        "gstin_tax_id": "27AAACT2727Q1ZW",
        "date": "2026-03-15",
        "due_date": "2026-04-15",
        "currency": "INR",
        "subtotal": 157118.64,
        "tax_amount": 28281.36,
        "total_amount": 185400.00,
        "payment_status": "Pending Approval",
        "department": "Finance",
        "confidence_score": 98.4,
        "detected_language": "English",
        "line_items": [
            {
                "item_id": 1,
                "description": "High-Performance GPU Compute Instances (NVIDIA H100 Cluster - 480 hrs)",
                "quantity": 480.0,
                "unit_price": 240.0,
                "total": 115200.0,
                "hsn_sac": "998315"
            },
            {
                "item_id": 2,
                "description": "Managed Kubernetes Orchestration & Indic OCR Pipeline Hosting",
                "quantity": 1.0,
                "unit_price": 28000.0,
                "total": 28000.0,
                "hsn_sac": "998313"
            },
            {
                "item_id": 3,
                "description": "High-Throughput Enterprise S3 Object Storage (10 TB Multi-AZ)",
                "quantity": 10.0,
                "unit_price": 1391.86,
                "total": 13918.64,
                "hsn_sac": "998319"
            }
        ],
        "key_attributes": {
            "po_reference": "PO-SARVAM-2026-041",
            "payment_terms": "Net 30 Days",
            "igst_rate": "18.0%"
        },
        "risk_assessment": {
            "risk_level": "MEDIUM",
            "flags": ["High-value invoice exceeding ₹1,00,000 threshold"],
            "reasoning": "Standard cloud infrastructure charges, flagged automatically for CFO tier authorization."
        },
        "summary": "Cloud compute and GPU cluster invoice from Tata Consultancy Services for ₹1,85,400.00 with 18% IGST.",
        "raw_text": """TATA CONSULTANCY SERVICES LIMITED
Corporate Office: TCS House, Raveline Street, Fort, Mumbai - 400001
GSTIN: 27AAACT2727Q1ZW | PAN: AAACT2727Q

TAX INVOICE
Invoice No: TCS-IN-2026-9842                     Invoice Date: 15-Mar-2026
PO Reference: PO-SARVAM-2026-041                 Due Date: 15-Apr-2026

Billed To:
Sarvam AI Technologies Pvt Ltd
RMZ Titanium, Ground Floor, Old Airport Road, Bengaluru, Karnataka 560008
GSTIN: 29AAMCS8921R1ZT

Description of Services                    SAC Code   Qty   Unit Rate    Total (INR)
1. High-Performance GPU Compute Instances   998315     480   240.00       1,15,200.00
2. Managed Kubernetes Orchestration        998313       1    28,000.00      28,000.00
3. Enterprise Object Storage (10 TB)       998319      10    1,391.86       13,918.64

Subtotal:                                                                1,57,118.64
Integrated GST (IGST @ 18%):                                               28,281.36
TOTAL INVOICE AMOUNT (INR):                                              1,85,400.00
Amount in words: One Lakh Eighty Five Thousand Four Hundred Rupees Only.

Bank Account: HDFC Bank Ltd, Account: 00030350019284, IFSC: HDFC0000003
Authorized Signatory: Rajesh Gopinathan
"""
    },
    {
        "filename": "Apollo_Diagnostics_Comprehensive_Blood_Panel.pdf",
        "doc_type": "Medical Report",
        "title": "Apollo Diagnostics - Clinical Chemistry & Metabolic Biomarker Report",
        "document_number": "APL-LAB-2026-4401",
        "entity_name": "Apollo Diagnostics Laboratories",
        "recipient_name": "Sunil Verma (Age: 48, Male)",
        "entity_address": "Apollo Hospitals Campus, Greams Road, Thousand Lights, Chennai 600006",
        "gstin_tax_id": "33AAACA3849P1Z8",
        "date": "2026-03-20",
        "due_date": "N/A",
        "currency": "INR",
        "subtotal": 3800.00,
        "tax_amount": 0.00,
        "total_amount": 3800.00,
        "payment_status": "Paid",
        "department": "Healthcare",
        "confidence_score": 96.2,
        "detected_language": "English",
        "line_items": [
            {
                "item_id": 1,
                "description": "Fasting Blood Glucose (FBG) - 168 mg/dL [Normal: 70 - 99]",
                "quantity": 1.0,
                "unit_price": 450.0,
                "total": 450.0,
                "hsn_sac": "999312"
            },
            {
                "item_id": 2,
                "description": "Glycated Hemoglobin (HbA1c) - 8.4% [Normal: < 5.7%]",
                "quantity": 1.0,
                "unit_price": 950.0,
                "total": 950.0,
                "hsn_sac": "999312"
            },
            {
                "item_id": 3,
                "description": "Serum Creatinine & eGFR Renal Profile",
                "quantity": 1.0,
                "unit_price": 1100.0,
                "total": 1100.0,
                "hsn_sac": "999312"
            },
            {
                "item_id": 4,
                "description": "Comprehensive Lipid Biomarker Panel (Cholesterol: 242 mg/dL)",
                "quantity": 1.0,
                "unit_price": 1300.0,
                "total": 1300.0,
                "hsn_sac": "999312"
            }
        ],
        "key_attributes": {
            "patient_id": "PID-90821",
            "fasting_glucose": "168 mg/dL (Elevated)",
            "hba1c": "8.4% (Elevated)",
            "total_cholesterol": "242 mg/dL (High)",
            "physician_referral": "Dr. Arvind Rao, MD"
        },
        "risk_assessment": {
            "risk_level": "HIGH",
            "flags": [
                "Critically elevated HbA1c (8.4%) indicating uncontrolled hyperglycemia",
                "Elevated fasting glucose (168 mg/dL)"
            ],
            "reasoning": "Clinical biomarkers exceed safe thresholds; triggers priority medical consultation."
        },
        "summary": "Laboratory diagnostic report for patient Sunil Verma showing elevated Fasting Blood Glucose (168 mg/dL) and HbA1c (8.4%).",
        "raw_text": """APOLLO DIAGNOSTICS - CLINICAL BIOCHEMISTRY DIVISION
Chennai Central Laboratory: Greams Lane, Chennai - 600006
NABL Accredited Laboratory No. MC-2041

PATIENT CLINICAL REPORT
Patient Name: Sunil Verma                    Age/Gender: 48 Y / Male
UHID / Patient ID: PID-90821                 Sample Collected: 20-Mar-2026 07:30 AM
Referred By: Dr. Arvind Rao, MD              Report Released: 20-Mar-2026 02:15 PM

INVESTIGATION                          RESULT     UNIT      BIOLOGICAL REFERENCE
Fasting Blood Glucose (Hexokinase)    168.0      mg/dL     70.0 - 99.0   [HIGH]
HbA1c (Glycosylated Hemoglobin)         8.4      %         < 5.7 (Normal) [HIGH]
                                                           5.7 - 6.4 (Prediabetes)
                                                           >= 6.5 (Diabetes Action)
Serum Creatinine                        1.02     mg/dL     0.70 - 1.30   [NORMAL]
Estimated GFR (CKD-EPI)                94        mL/min    > 90          [NORMAL]
Total Cholesterol                      242       mg/dL     < 200         [BORDERLINE HIGH]
Triglycerides                          195       mg/dL     < 150         [HIGH]

CLINICAL IMPRESSION:
Laboratory findings show marked glycemic dysregulation (HbA1c 8.4%, Fasting Glucose 168 mg/dL).
Immediate clinical follow-up recommended for diabetic management adjustments.

Pathologist: Dr. Meenakshi Sundaram, MD (Path)
Verified by Laboratory Director
"""
    },
    {
        "filename": "Reliance_Retail_Commercial_Purchase_Order.pdf",
        "doc_type": "Purchase Order",
        "title": "Reliance Retail Ltd - Commercial Enterprise Purchase Order",
        "document_number": "PO-RRL-2026-7719",
        "entity_name": "Reliance Retail Limited",
        "recipient_name": "Apex Electronic Logistics LLP",
        "entity_address": "Maker Chambers IV, 222 Nariman Point, Mumbai, Maharashtra 400021",
        "gstin_tax_id": "27AAACR4051B1Z3",
        "date": "2026-03-22",
        "due_date": "2026-04-20",
        "currency": "INR",
        "subtotal": 377118.64,
        "tax_amount": 67881.36,
        "total_amount": 445000.00,
        "payment_status": "Pending Approval",
        "department": "Procurement",
        "confidence_score": 97.8,
        "detected_language": "English",
        "line_items": [
            {
                "item_id": 1,
                "description": "Barcode & Smart RFID Handheld Scanners for Fulfillment Centers",
                "quantity": 50.0,
                "unit_price": 5200.0,
                "total": 260000.0,
                "hsn_sac": "847190"
            },
            {
                "item_id": 2,
                "description": "Thermal Shipping Label Printers (Industrial 300 DPI)",
                "quantity": 10.0,
                "unit_price": 11711.86,
                "total": 117118.64,
                "hsn_sac": "844332"
            }
        ],
        "key_attributes": {
            "delivery_location": "Bhiwandi Mega Warehouse DC-4, Maharashtra",
            "incoterms": "DDP Bhiwandi",
            "lead_time": "14 business days"
        },
        "risk_assessment": {
            "risk_level": "HIGH",
            "flags": [
                "Expenditure of ₹4,45,000 exceeds standard departmental procurement limit (₹2,50,000)"
            ],
            "reasoning": "Large capital procurement order requiring multi-stage executive approval."
        },
        "summary": "Commercial Purchase Order issued by Reliance Retail Limited for warehouse automation hardware totaling ₹4,45,000.00.",
        "raw_text": """RELIANCE RETAIL LIMITED
Registered Office: 3rd Floor, Court House, Lokmanya Tilak Marg, Dhobi Talao, Mumbai - 400002
GSTIN: 27AAACR4051B1Z3 | CIN: U01100MH1999PLC120563

COMMERCIAL PURCHASE ORDER
PO Number: PO-RRL-2026-7719                       PO Date: 22-Mar-2026
Vendor: Apex Electronic Logistics LLP            Delivery Due: 20-Apr-2026
GSTIN: 27AABCA9012J1Z2                           Payment Terms: Net 45 Days

Shipping Address:
Reliance Retail Mega Fulfillment Center, Building D-4, Bhiwandi Logistics Park,
Thane District, Maharashtra 421302

Item   Description                                HSN Code  Qty  Rate (INR)     Amount (INR)
1      Handheld RFID Barcode Terminals (Android)   847190    50   5,200.00       2,60,000.00
2      Industrial Thermal Label Printers 300DPI   844332    10   11,711.86      1,17,118.64

Subtotal:                                                                       3,77,118.64
CGST @ 9%:                                                                        33,940.68
SGST @ 9%:                                                                        33,940.68
TOTAL ORDER VALUE:                                                              4,45,000.00

Special Instructions:
All consignments must be accompanied by triplicate delivery challans and test warranty certificates.
Approved by: Head of Supply Chain Procurement, Western Region
"""
    },
    {
        "filename": "BESCOM_Karnataka_Electricity_Bill_Bilingual.pdf",
        "doc_type": "Utility Bill",
        "title": "BESCOM - Bangalore Electricity Supply Commercial Utility Bill (Bilingual Kannada/English)",
        "document_number": "BESCOM-LT-2026-10928",
        "entity_name": "Bangalore Electricity Supply Company Ltd (BESCOM)",
        "recipient_name": "Sarvam AI Research Labs",
        "entity_address": "K.R. Circle, Nrupathunga Road, Bengaluru, Karnataka 560001",
        "gstin_tax_id": "29AABCB1829L1Z5",
        "date": "2026-03-10",
        "due_date": "2026-03-25",
        "currency": "INR",
        "subtotal": 52140.00,
        "tax_amount": 4692.60,
        "total_amount": 56832.60,
        "payment_status": "Pending Approval",
        "department": "Operations",
        "confidence_score": 95.5,
        "detected_language": "Kannada & English (Multilingual Indic)",
        "line_items": [
            {
                "item_id": 1,
                "description": "Commercial LT-2 Tariff Energy Consumption (5,840 Units @ ₹8.25/unit)",
                "quantity": 5840.0,
                "unit_price": 8.25,
                "total": 48180.0,
                "hsn_sac": "996911"
            },
            {
                "item_id": 2,
                "description": "Sanctioned Load Fixed Charges (25 kW @ ₹158.40/kW)",
                "quantity": 25.0,
                "unit_price": 158.4,
                "total": 3960.0,
                "hsn_sac": "996911"
            },
            {
                "item_id": 3,
                "description": "Karnataka State Electricity Duty (KED @ 9%)",
                "quantity": 1.0,
                "unit_price": 4692.6,
                "total": 4692.6,
                "hsn_sac": "996911"
            }
        ],
        "key_attributes": {
            "consumer_account": "CA-883920194",
            "meter_number": "KA-BLR-89211",
            "sanctioned_load": "25 kW Commercial",
            "bilingual_script": "Kannada / ಕನ್ನಡ & English"
        },
        "risk_assessment": {
            "risk_level": "LOW",
            "flags": ["Due date approaching within 5 days for early payment rebate"],
            "reasoning": "Routine recurring state utility invoice with standard tariff schedule."
        },
        "summary": "BESCOM commercial electricity consumption bill for ₹56,832.60 featuring multilingual Indic Kannada and English breakdown.",
        "raw_text": """ಬೆಂಗಳೂರು ವಿದ್ಯುತ್ ಸರಬರಾಜು ಕಂಪನಿ ನಿಯಮಿತ (ಬೆಸ್ಕಾಂ)
BANGALORE ELECTRICITY SUPPLY COMPANY LIMITED (BESCOM)
K.R. Circle, Bengaluru - 560001 | GSTIN: 29AABCB1829L1Z5

ವಿದ್ಯುತ್ ಬಿಲ್ / ELECTRICITY BILL (COMMERCIAL LT-2)
ಗ್ರಾಹಕರ ಸಂಖ್ಯೆ / Account ID: CA-883920194            ಬಿಲ್ ದಿನಾಂಕ / Bill Date: 10-Mar-2026
ಮೀಟರ್ ಸಂಖ್ಯೆ / Meter No: KA-BLR-89211                ಕೊನೆಯ ದಿನಾಂಕ / Due Date: 25-Mar-2026

ಗ್ರಾಹಕರ ಹೆಸರು ಮತ್ತು ವಿಳಾಸ / Consumer Name:
Sarvam AI Research Labs
RMZ Titanium, HAL Airport Road, Bengaluru - 560008

ಹಿಂದಿನ ಓದುವಿಕೆ / Previous Reading: 42,100            ಪ್ರಸ್ತುತ ಓದುವಿಕೆ / Present Reading: 47,940
ಬಳಕೆಯ ಯುನಿಟ್‌ಗಳು / Consumed Units: 5,840 kWh         ಮಂಜೂರಾದ ಲೋಡ್ / Sanctioned Load: 25.00 kW

ವಿವರಣೆ / Description                                             ಮೊತ್ತ / Amount (INR)
1. ವಿದ್ಯುತ್ ಬಳಕೆ ಶುಲ್ಕ / Energy Charges (5,840 units @ 8.25)          48,180.00
2. ನಿಗದಿತ ಶುಲ್ಕ / Fixed Charges (25 kW @ 158.40)                       3,960.00
3. ವಿದ್ಯುತ್ ತೆರಿಗೆ / Electricity Duty (9%)                              4,692.60

ಒಟ್ಟು ಪಾವತಿಸಬೇಕಾದ ಮೊತ್ತ / TOTAL PAYABLE AMOUNT:                         56,832.60
ಸಮಯಕ್ಕೆ ಪಾವತಿಸಿದರೆ ರಿಯಾಯಿತಿ / Prompt Payment Discount:                  ₹ 568.00

ಪಾವತಿ ವಿಧಾನ: UPI, NetBanking, BBPS ಮೂಲಕ ಪಾವತಿಸಿ.
ಸಹಾಯಕ ಕಾರ್ಯನಿರ್ವಾಹಕ ಎಂಜಿನಿಯರ್, ಬೆಸ್ಕಾಂ ಇಂದಿರಾನಗರ ಉಪ-ವಿಭಾಗ
"""
    },
    {
        "filename": "Infosys_Master_Services_Vendor_Agreement.pdf",
        "doc_type": "Contract",
        "title": "Infosys Technologies - Master Services & AI Model Licensing Contract",
        "document_number": "MSA-INFY-2026-118",
        "entity_name": "Infosys Limited",
        "recipient_name": "Sarvam AI Solutions",
        "entity_address": "Electronics City, Hosur Road, Bengaluru, Karnataka 560100",
        "gstin_tax_id": "29AAACI4798H1Z8",
        "date": "2026-03-01",
        "due_date": "2027-02-28",
        "currency": "INR",
        "subtotal": 1200000.00,
        "tax_amount": 216000.00,
        "total_amount": 1416000.00,
        "payment_status": "Pending Approval",
        "department": "Legal",
        "confidence_score": 99.1,
        "detected_language": "English",
        "line_items": [
            {
                "item_id": 1,
                "description": "Annual Enterprise Multilingual AI Vision & Document OCR License (12 Months)",
                "quantity": 1.0,
                "unit_price": 1200000.0,
                "total": 1200000.0,
                "hsn_sac": "997331"
            }
        ],
        "key_attributes": {
            "effective_term": "12 Months (01-Mar-2026 to 28-Feb-2027)",
            "governing_law": "Courts of Bengaluru, Karnataka, India",
            "indemnity_cap": "₹ 50,00,000",
            "confidentiality_duration": "5 Years post termination"
        },
        "risk_assessment": {
            "risk_level": "HIGH",
            "flags": [
                "Contract commitment exceeds ₹10,00,000 threshold",
                "Legal review mandatory for indemnity clause cap"
            ],
            "reasoning": "Annual strategic licensing agreement requiring legal counsel sign-off."
        },
        "summary": "Master Services Agreement between Infosys Limited and Sarvam AI Solutions for enterprise Indic vision and document OCR licensing totaling ₹14,16,000.00.",
        "raw_text": """MASTER SERVICES & SOFTWARE LICENSING AGREEMENT
Reference No: MSA-INFY-2026-118
Date of Execution: March 01, 2026

BETWEEN:
INFOSYS LIMITED, a corporation organized under the laws of India, having its principal place of business at Electronics City, Hosur Road, Bengaluru - 560100 (hereinafter referred to as 'INFOSYS')
AND
SARVAM AI SOLUTIONS PVT LTD, having its registered office at Bengaluru, Karnataka (hereinafter referred to as 'VENDOR').

1. SCOPE OF SERVICES & LICENSE:
Vendor grants to Infosys a non-exclusive, enterprise-wide license to integrate Sarvam Indic Document Intelligence & OCR APIs across banking, telecom, and citizen services workflows.

2. COMMERCIAL CONSIDERATION:
Annual Enterprise Licensing Fee: INR 12,00,000.00 (Twelve Lakhs Rupees)
Applicable Goods & Services Tax (GST @ 18%): INR 2,16,000.00
TOTAL CONTRACT VALUE: INR 14,16,000.00 (Fourteen Lakhs Sixteen Thousand Rupees)

3. INDEMNITY & LIMITATION OF LIABILITY:
Either party's maximum aggregate liability shall be capped at INR 50,00,000.00 (Fifty Lakhs Rupees), excluding breaches of confidentiality and intellectual property rights.

4. GOVERNING LAW & JURISDICTION:
This Agreement shall be governed by the laws of India, with exclusive jurisdiction in the courts of Bengaluru, Karnataka.

IN WITNESS WHEREOF, the parties hereto have executed this Agreement by their authorized representatives.
For Infosys Limited: Salil Parekh, CEO & MD
For Sarvam AI: Pratyush Kumar / Vivek Raghavan, Founders
"""
    }
]

def load_sample_documents_into_system():
    """
    Populates database with sample documents and triggers workflow evaluations.
    """
    count = 0
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        existing = cursor.fetchone()[0]

    # If documents already loaded, don't duplicate unless forced
    if existing > 0:
        return existing

    for doc in SAMPLE_DOCUMENTS:
        doc_id = db.insert_document(doc, raw_text=doc["raw_text"], file_path=f"samples/{doc['filename']}")
        # Trigger workflows
        workflow_engine.evaluate_document_workflows(doc_id, doc)
        count += 1

    return count
