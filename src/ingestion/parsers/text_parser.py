from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement

class TextParser:
    """
    Worker responsible for extracting content from plain text 
    and markdown files.
    """
    def parse(self, path: Path) -> List[DocumentElement]:
        """
        Reads the file and splits it into 'chunks' based on double newlines.
        This prevents sending a 100-page text file as one single element.
        """
        try:
            # Read the content of the file
            content = path.read_text(encoding="utf-8")
            
            # Split content into paragraphs (double newline) 
            # to maintain some structure for the AI
            chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
            
            elements = []
            for i, chunk in enumerate(chunks):
                elements.append(
                    DocumentElement(
                        element_type="text",
                        content=chunk,
                        source_file=path.name,
                        metadata={"chunk_index": i}
                    )
                )
            return elements
            
        except Exception as e:
            print(f"❌ Error parsing text file {path.name}: {e}")
            return []