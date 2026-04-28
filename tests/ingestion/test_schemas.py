import pytest
from src.ingestion.schemas import DocumentElement, IngestionResponse

def test_valid_element_creation():
    """Test that a correct set of data creates a DocumentElement successfully."""
    element = DocumentElement(
        element_type="header",
        content="Quarterly Financial Report",
        source_file="finance_2024.pdf",
        page_number=1,
        metadata={"font": "Helvetica"}
    )
    assert element.element_type == "header"
    assert element.source_file == "finance_2024.pdf"

def test_invalid_element_creation():
    """Test that Pydantic raises an error when required fields are missing."""
    with pytest.raises(ValueError): # Pydantic raises ValidationError, which is a subclass of ValueError
        DocumentElement(
            source_file="broken.txt"
            # element_type and content are missing!
        )

def test_ingestion_response_wrapper():
    """Test that the master response wrapper works correctly."""
    element = DocumentElement(
        element_type="text",
        content="Hello World",
        source_file="test.txt"
    )
    response = IngestionResponse(
        total_elements=1,
        files_processed=["test.txt"],
        elements=[element]
    )
    assert response.total_elements == 1
    assert len(response.elements) == 1