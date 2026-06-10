import zipfile
import uuid
from pathlib import Path
from typing import List

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
            # Create a guaranteed unique folder for this specific zip to avoid collisions
            unique_id = uuid.uuid4().hex
            zip_folder = self.temp_dir / f"{path.stem}_{unique_id}"
            zip_folder.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(path, 'r') as zip_ref:
                # Extract all files securely
                zip_ref.extractall(zip_folder)
                
                # Recursively find all files extracted
                for file in zip_folder.rglob("*"):
                    if file.is_file():
                        # Skip hidden files and macOS system folders
                        if file.name.startswith('.') or '__MACOSX' in file.parts:
                            continue
                        extracted_files.append(file)
            
            print(f"📦 Unzipped {path.name}: found {len(extracted_files)} files.")
            return extracted_files

        except Exception as e:
            print(f"❌ Error unpacking ZIP {path.name}: {e}")
            return []