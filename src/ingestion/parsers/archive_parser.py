import zipfile
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement

class ArchiveParser:
    """
    Archive Worker responsible for unpacking ZIP files.
    Returns a list of paths to the extracted files for further processing.
    """
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def parse(self, path: Path) -> List[Path]:
        """
        Unpacks the ZIP file into the temp directory.
        Returns a list of Paths to the extracted files.
        """
        extracted_files = []
        try:
            # Create a unique folder for this specific zip to avoid collisions
            zip_folder = self.temp_dir / path.stem
            zip_folder.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(zip_folder)
                
                # Recursively find all files extracted
                for file in zip_folder.rglob("*"):
                    if file.is_file():
                        extracted_files.append(file)
            
            print(f"📦 Unzipped {path.name}: found {len(extracted_files)} files.")
            return extracted_files

        except Exception as e:
            print(f"❌ Error unpacking ZIP {path.name}: {e}")
            return []