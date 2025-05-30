import subprocess
from pathlib import Path

def excel_to_pdf(xlsx_path: Path) -> Path:
    pdf_path = xlsx_path.with_suffix(".pdf")
    subprocess.check_call([
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(xlsx_path.parent), str(xlsx_path)
    ])
    return pdf_path
