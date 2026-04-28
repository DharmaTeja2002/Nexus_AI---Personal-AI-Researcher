import fitz  # PyMuPDF
import camelot
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement

class PDFParser:
    """
    High-performance PDF worker. 
    Extracts text layout and structured tables.
    """
    def parse(self, path: Path) -> List[DocumentElement]:
        elements = []
        
        try:
            # 1. Extract Text using PyMuPDF
            doc = fitz.open(path)
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                if text.strip():
                    elements.append(
                        DocumentElement(
                            element_type="text",
                            content=text.strip(),
                            source_file=path.name,
                            page_number=page_num,
                            metadata={"method": "pymupdf"}
                        )
                    )
            doc.close()

            # 2. Extract Tables using Camelot
            # 'flavor="stream"' is used for tables without visible lines
            # 'flavor="lattice"' is used for tables with clear grid lines
            tables = camelot.read_pdf(str(path), pages='all', flavor='stream')
            
            for i, table in enumerate(tables):
                # Convert the Pandas DataFrame to a CSV-like string
                # This 'linearizes' the table so the AI can reason over it
                table_text = table.df.to_csv(index=False, sep="|")
                
                elements.append(
                    DocumentElement(
                        element_type="table",
                        content=table_text,
                        source_file=path.name,
                        page_number=table.page,
                        metadata={"table_index": i, "method": "camelot"}
                    )
                )
            
            return elements

        except Exception as e:
            print(f"❌ Error parsing PDF {path.name}: {e}")
            return []