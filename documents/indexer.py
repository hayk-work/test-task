import os
import pickle
import uuid

import faiss
import numpy as np
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

from config import settings


if not os.path.exists(settings.FAISS_INDEX_DIR):
    os.makedirs(settings.FAISS_INDEX_DIR)


def index_document(content: str):
    """
    Index a document by breaking it into chunks and creating a FAISS index for fast similarity search.

    The document content is split into chunks based on newlines. Each chunk is then transformed into
    a vector representation using the TF-IDF vectorizer. These vectors are added to a FAISS index
    to enable efficient similarity search. The FAISS index and document chunks are then saved, and a
    unique document ID is returned.

    Args:
        content (str): The text content of the document to be indexed. This content is split into
                       chunks based on newline characters.

    Returns:
        str: A unique identifier for the indexed document, which can be used to load and query the
             indexed data later.
    """
    chunks = content.split("\n")

    vectorizer = TfidfVectorizer(stop_words="english")
    embeddings = vectorizer.fit_transform(chunks).toarray()

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))

    document_id = save_faiss_index(index, chunks, vectorizer)
    return document_id


def save_faiss_index(index: faiss.Index, chunks: List[str], vectorizer) -> str:
    """
    Save the FAISS index to a file on disk.

    Args:
        index (faiss.Index): The FAISS index object to save.
        chunks (List[str]): The document chunks that the index corresponds to.

    Returns:
        document_id (str): A unique identifier for the saved document/index.
    """
    document_id = str(uuid.uuid4())
    if not os.path.exists(settings.FAISS_INDEX_DIR):
        os.makedirs(settings.FAISS_INDEX_DIR)

    faiss.write_index(index, os.path.join(settings.FAISS_INDEX_DIR, f"{document_id}.index"))

    with open(os.path.join(settings.FAISS_INDEX_DIR, f"{document_id}_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    with open(os.path.join(settings.FAISS_INDEX_DIR, f"{document_id}_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    return document_id
