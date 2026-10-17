import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from backend.config import SAMPLES_DIR

def create_sample_pdf(file_path: Path, title: str, text_content: str):
    """Generates a styled, clean PDF document using matplotlib backend."""
    with PdfPages(str(file_path)) as pdf:
        fig = plt.figure(figsize=(8.5, 11), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        
        # Border
        ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
        ax.axis('off')
        
        # Header banner
        fig.text(0.08, 0.92, title, fontsize=14, weight='bold', color='#0f172a')
        fig.text(0.08, 0.89, "SARVAM AI - ENTERPRISE DOCUMENT INTELLIGENCE", fontsize=8, weight='bold', color='#6366f1')
        
        # Horizontal line
        line = plt.Line2D([0.08, 0.92], [0.87, 0.87], transform=fig.transFigure, color='#cbd5e1', linewidth=1.5)
        fig.add_artist(line)
        
        # Main body text
        wrapped_text = "\n".join([line for line in text_content.strip().split("\n")[:48]])
        fig.text(0.08, 0.84, wrapped_text, fontsize=9.5, fontfamily='monospace', verticalalignment='top', color='#1e293b')
        
        # Footer
        fig.text(0.08, 0.05, "Digitized & Processed via Sarvam AI Multimodal Pipeline", fontsize=8, color='#94a3b8')
        fig.text(0.85, 0.05, "Page 1 of 1", fontsize=8, color='#94a3b8')
        
        pdf.savefig(fig)
        plt.close(fig)

def generate_all_sample_pdfs():
    """Generates all sample PDF files into the samples/ folder."""
    from backend.sample_data import SAMPLE_DOCUMENTS
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    
    for sample in SAMPLE_DOCUMENTS:
        target_path = SAMPLES_DIR / sample["filename"]
        if not target_path.exists():
            create_sample_pdf(target_path, sample["title"], sample["raw_text"])

if __name__ == "__main__":
    generate_all_sample_pdfs()
    print("All sample PDFs generated successfully.")
