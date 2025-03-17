from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Document(Base):
    """
    Model to store uploaded document metadata.

    Attributes:
    id (int): Primary key of the document.
    filename (str): Original filename of the uploaded document.
    file_path (str): Path where the document is stored on the server.
    uploaded_by (int): Foreign key linking to the user who uploaded the document.
    created_at (datetime): Timestamp of when the document was uploaded.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    uploaded_by = relationship("User", back_populates="documents")
