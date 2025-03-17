import os
import pickle

import faiss
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

from config import settings


def retrieve_relevant_chunks(query: str, document_id: str):
    """
    Retrieve the most relevant chunks from a document based on a user query using FAISS similarity search.

    This function loads the FAISS index and associated chunks for a given document ID. It then transforms
    the user's query into a vector using TF-IDF, searches the FAISS index for the top-k most similar chunks,
    and returns those chunks.

    Args:
        query (str): The search query entered by the user, which will be used to find relevant document chunks.
        document_id (str): The unique identifier of the document whose chunks are to be searched.

    Returns:
        List[str]: A list of the most relevant chunks (text segments) from the document, based on the query.
    """
    index, chunks, vectorizer = load_faiss_index_and_chunks(document_id)
    query_vector = vectorizer.transform([query]).toarray().astype(np.float32)

    _, indices = index.search(query_vector, k=5)
    relevant_chunks = [chunks[i] for i in indices[0]]

    return relevant_chunks


def load_faiss_index_and_chunks(document_id: str):
    """
    Load the FAISS index, document chunks, and the trained TF-IDF vectorizer.
    """

    with open(os.path.join(settings.FAISS_INDEX_DIR, f"{document_id}_chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)

    with open(os.path.join(settings.FAISS_INDEX_DIR, f"{document_id}_vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    index = faiss.read_index(f"{settings.FAISS_INDEX_DIR}/{document_id}.index")

    return index, chunks, vectorizer
