from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentElement(BaseModel):
    """
    The smallest unit of data in NexusAI.
    Whether it's a paragraph from a PDF or a row from a CSV, 
    it must fit into this model.
    """
    # The type of content (e.g., "text", "table", "header", "list", "caption")
    element_type: str = Field(..., description="The category of the extracted element")
    
    # The actual content extracted
    content: str = Field(..., description="The raw text or linearized table content")
    
    # Which file did this come from?
    source_file: str = Field(..., description="The name of the original file")
    
    # Where in the file was this found? (Optional for text files)
    page_number: Optional[int] = Field(None, description="The page number if applicable")
    
    # Any extra info (e.g., table columns, image resolution, email sender)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional key-value pairs")
    
    # When was this processed?
    processed_at: datetime = Field(default_factory=datetime.now)

class IngestionResponse(BaseModel):
    """
    The final wrapper for the entire ingestion process.
    This is what will eventually be saved as nexus_memory_dump.json
    """
    project_name: str = "NexusAI"
    total_elements: int
    files_processed: List[str]
    elements: List[DocumentElement]
