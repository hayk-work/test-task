from pydantic import BaseModel


class DocumentQuery(BaseModel):
    """
    Schema for querying a document.

    Attributes:
    query (str): The question to ask based on the document.
    document_id (int): ID of the document to query.
    """
    query: str
    document_id: int
