# AI Document Management System

This project implements a Retrieval-Augmented Generation (RAG) pipeline for uploading, indexing, and querying documents. It integrates with OpenAI's API to generate contextually relevant answers based on the document content. The application is built using FastAPI, SQLAlchemy, FAISS, and integrates access control using Oso.

## Features
- Document upload and processing (txt, pdf, docx)
- Text extraction and indexing using FAISS
- Contextual question answering via OpenAI's API
- Admin access to all documents
- User-specific access control based on Oso policies


## Installation

1. Clone the repository:
   ```bash
   https://github.com/hayk-work/test-task.git
   cd test-task

2. Set up a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the project dependencies:
    pip install -r requirements.txt
   
4. Set up the environment variables as shown in .env.example.

5. Initialize Alembic:
    alembic init alembic

6. Configure Alembic. Open alembic.ini and configure your SQLAlchemy database URL:
    [alembic]
    # Replace this with your actual database URL
    sqlalchemy.url = postgresql://username:password@localhost/dbname

7. Modify alembic/env.py:
   Add this 3 lines:
    from database import Base
    from users import models
    from documents import models
   And update 'target_metadata':
    target_metadata = Base.metadata

8. Create Migration
    alembic revision --autogenerate -m "Initial migration"

9. Apply Migration:
    alembic upgrade head

10. Run the FastAPI application:
   uvicorn app.main:app --reload
   
11. Access the application at http://127.0.0.1:8000.
