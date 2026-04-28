import asyncio
import magic
from pathlib import Path
from typing import AsyncGenerator, List
from src.core.config import settings
from src.ingestion.schemas import DocumentElement
from src.ingestion.parsers.text_parser import TextParser
from src.ingestion.parsers.pdf_parser import PDFParser
from src.ingestion.parsers.tabular_parser import TabularParser
from src.ingestion.parsers.office_parser import OfficeParser
from src.ingestion.parsers.image_parser import ImageParser
from src.ingestion.parsers.archive_parser import ArchiveParser
from src.ingestion.parsers.media_parser import MediaParser

class UnifiedIngestor:
    def __init__(self):
        self.mime_detector = magic.Magic(mime=True)
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_FILES)
        
        # Initialize all Workers
        self.text_parser = TextParser()
        self.pdf_parser = PDFParser()
        self.tabular_parser = TabularParser()
        self.office_parser = OfficeParser()
        self.image_parser = ImageParser()
        self.archive_parser = ArchiveParser(settings.TEMP_DIR)
        self.media_parser = MediaParser()
        
        self.parser_map = {
            "text/plain": (self.text_parser, self.text_parser.parse),
            "text/markdown": (self.text_parser, self.text_parser.parse),
            "text/csv": (self.tabular_parser, self.tabular_parser.parse),
            "application/pdf": (self.pdf_parser, self.pdf_parser.parse),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": (self.tabular_parser, self.tabular_parser.parse),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (self.office_parser, self.office_parser.parse),
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": (self.office_parser, self.office_parser.parse),
            "image/jpeg": (self.image_parser, self.image_parser.parse),
            "image/png": (self.image_parser, self.image_parser.parse),
            "application/zip": (self.archive_parser, self.archive_parser.parse),
            "audio/mpeg": (self.media_parser, self.media_parser.parse),
            "audio/wav": (self.media_parser, self.media_parser.parse),
            "audio/x-wav": (self.media_parser, self.media_parser.parse),
            "video/mp4": (self.media_parser, self.media_parser.parse),
            "video/x-matroska": (self.media_parser, self.media_parser.parse),
            "video/quicktime": (self.media_parser, self.media_parser.parse),
        }

    async def ingest_file(self, file_path: Path) -> List[DocumentElement]:
        """
        Processes a single file. Returns a List of elements.
        This is a coroutine, so it is compatible with asyncio.as_completed.
        """
        async with self.semaphore:
            mime_type = self.mime_detector.from_file(str(file_path))
            print(f"🔍 Processing: {file_path.name} ({mime_type})")

            parser_info = self.parser_map.get(mime_type)

            if not parser_info or parser_info[0] is None:
                print(f"⚠️ No active parser for {mime_type}. Skipping.")
                return []

            parser_instance, parse_method = parser_info
            # Run the blocking parser in a thread
            result = await asyncio.to_thread(parse_method, file_path)

            # --- RECURSIVE ARCHIVE LOGIC ---
            if result and isinstance(result[0], Path):
                print(f"📦 Archive detected: {file_path.name}. Extracting {len(result)} files...")
                all_inner_elements = []
                for extracted_path in result:
                    # Recursively await the ingestion of the inner file
                    inner_elements = await self.ingest_file(extracted_path)
                    all_inner_elements.extend(inner_elements)
                return all_inner_elements
            
            # Standard case: result is already a List[DocumentElement]
            return result

    async def process_all(self, input_folder: Path) -> AsyncGenerator[DocumentElement, None]:
        """
        The Master Streamer. 
        Uses as_completed to run coroutines and yields elements one by one.
        """
        files = [
            f for f in input_folder.iterdir() 
            if f.is_file() and ":Zone.Identifier" not in f.name
        ]
        
        # Create a list of coroutines
        tasks = [self.ingest_file(f) for f in files]
        
        for coro in asyncio.as_completed(tasks):
            elements = await coro # Wait for one file (and its inner zip files) to finish
            for element in elements:
                yield element