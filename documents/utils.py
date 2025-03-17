import io
from pdfminer.high_level import extract_text
from docx import Document


async def extract_text_from_file(file):
    """
    Extracts text from TXT, PDF, or DOCX files.
    """
    if file.content_type == "text/plain":
        return await extract_text_from_txt(file)
    elif file.content_type == "application/pdf":
        return extract_text_from_pdf(await file.read())  # Read all bytes first
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(await file.read())  # Read all bytes first
    else:
        raise ValueError("Unsupported file format")


async def extract_text_from_txt(file):
    """
    Extracts text from a plain text file.
    """
    return (await file.read()).decode("utf-8")


def extract_text_from_pdf(pdf_bytes):
    """
    Extracts text from a PDF file using pdfminer.six.
    """
    pdf_stream = io.BytesIO(pdf_bytes)
    return extract_text(pdf_stream)


def extract_text_from_docx(docx_bytes):
    """
    Extracts text from a DOCX file using python-docx.
    """
    doc_stream = io.BytesIO(docx_bytes)
    doc = Document(doc_stream)
    return "\n".join([para.text for para in doc.paragraphs])
