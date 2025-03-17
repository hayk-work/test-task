import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from users.auth import get_current_user
from users.models import User
from documents.models import Document
from documents.retriever import retrieve_relevant_chunks
from documents.generator import generate_response
from documents.schemas import DocumentQuery
from documents.indexer import index_document
from documents.permissions import oso

router = APIRouter()

UPLOAD_DIR = "uploaded_documents/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a document, stores it, and indexes it for retrieval.

    Args:
        file (UploadFile): The file to upload.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Document ID and filename.
    """
    if file.content_type not in [
        "text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Generate a unique filename
    file_ext = file.filename.split('.')[-1]
    unique_filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Index document
    document_id = index_document(file_path)

    # Save metadata in DB
    new_document = Document(
        filename=file.filename, file_path=file_path, uploaded_by=current_user, document_id=document_id
    )
    db.add(new_document)
    await db.commit()

    return {"document_id": document_id, "filename": file.filename}


@router.post("/query")
async def query_document(
    document_query: DocumentQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Queries a document for relevant chunks and generates a response.

    Args:
        document_query (DocumentQuery): The query details including document_id.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: The AI-generated response.
    """
    # Fetch document
    result = await db.execute(select(Document).filter(Document.id == document_query.document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # OSO authorization check using policy.polar
    if not oso.is_allowed(current_user, "query", document):
        raise HTTPException(status_code=403, detail="Access denied")

    # Retrieve and generate response
    relevant_chunks = retrieve_relevant_chunks(document_query.query, document.document_id)
    answer = generate_response(relevant_chunks, document_query.query)

    return {"answer": answer}
