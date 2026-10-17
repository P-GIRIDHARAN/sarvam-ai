import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pdfplumber
from PIL import Image

class DocumentParser:
    """
    Multimodal document extractor:
    - Extracts text, tables, and layouts from PDF files using pdfplumber/pypdfium2
    - Handles raw text, scans, and images
    - Pre-processes documents for Sarvam Doc-AI & LLM structuring
    """

    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts clean text and metadata from PDF, TXT, or Image file.
        Returns (extracted_text, metadata_dict).
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        metadata = {
            "file_name": path.name,
            "file_size": os.path.getsize(file_path),
            "file_type": ext,
            "page_count": 1,
            "has_tables": False,
            "extraction_method": "unknown"
        }

        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path, metadata)
        elif ext in [".txt", ".csv", ".json", ".md"]:
            return DocumentParser._parse_text_file(file_path, metadata)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".webp"]:
            return DocumentParser._parse_image(file_path, metadata)
        else:
            # Fallback binary/text reader
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                metadata["extraction_method"] = "raw_text_read"
                return text, metadata
            except Exception as e:
                return f"[Unsupported File Format] {e}", metadata

    @staticmethod
    def _parse_pdf(file_path: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        full_text = []
        table_count = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata["page_count"] = len(pdf.pages)
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text.append(f"--- [Page {idx + 1}] ---\n" + page_text)
                    
                    # Extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        table_count += len(tables)
                        for t in tables:
                            table_md = DocumentParser._table_to_markdown(t)
                            full_text.append(f"\n[Detected Table]:\n{table_md}\n")

            metadata["has_tables"] = table_count > 0
            metadata["table_count"] = table_count
            metadata["extraction_method"] = "pdfplumber_layout_engine"
            return "\n".join(full_text), metadata
        except Exception as e:
            metadata["extraction_error"] = str(e)
            metadata["extraction_method"] = "pdf_fallback"
            return f"Error reading PDF: {e}", metadata

    @staticmethod
    def _parse_text_file(file_path: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        metadata["extraction_method"] = "text_file_stream"
        return text, metadata

    @staticmethod
    def _parse_image(file_path: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        try:
            img = Image.open(file_path)
            metadata["image_dimensions"] = f"{img.width}x{img.height}"
            metadata["image_format"] = img.format
            metadata["extraction_method"] = "image_metadata_vision"
            
            # Simulated OCR preview header for uploaded scans
            return f"[Scanned Image Document: {os.path.basename(file_path)}]\nDimensions: {img.width}x{img.height}\nFormat: {img.format}", metadata
        except Exception as e:
            metadata["extraction_error"] = str(e)
            return f"Error opening image: {e}", metadata

    @staticmethod
    def _table_to_markdown(table: list) -> str:
        if not table or not any(table):
            return ""
        lines = []
        headers = [str(col or "").strip().replace("\n", " ") for col in table[0]]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in table[1:]:
            cleaned_row = [str(col or "").strip().replace("\n", " ") for col in row]
            lines.append("| " + " | ".join(cleaned_row) + " |")
        return "\n".join(lines)

document_parser = DocumentParser()
