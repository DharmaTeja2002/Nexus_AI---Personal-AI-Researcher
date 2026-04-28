import pandas as pd
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement

class TabularParser:
    """
    Worker responsible for extracting data from CSV, TSV, and XLSX files.
    Converts tabular data into a linearized text format for AI reasoning.
    """
    def parse(self, path: Path) -> List[DocumentElement]:
        try:
            # 1. Determine the file type and read with Pandas
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(path)
            elif path.suffix.lower() == '.tsv':
                df = pd.read_csv(path, sep='\t')
            elif path.suffix.lower() == '.xlsx':
                df = pd.read_excel(path)
            else:
                # Fallback for files that might have wrong extensions but are CSVs
                df = pd.read_csv(path)

            # 2. Linearize the table
            # We convert the DataFrame to a CSV string using '|' as the separator
            # index=False removes the row numbers (0, 1, 2...) which usually confuse the AI
            linearized_table = df.to_csv(index=False, sep="|")
            
            # 3. Wrap in our Unified Schema
            return [
                DocumentElement(
                    element_type="table",
                    content=linearized_table,
                    source_file=path.name,
                    metadata={
                        "rows": len(df),
                        "cols": len(df.columns),
                        "columns": list(df.columns)
                    }
                )
            ]

        except Exception as e:
            print(f"❌ Error parsing tabular file {path.name}: {e}")
            return []