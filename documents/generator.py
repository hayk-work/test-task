from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_response(relevant_chunks: list, query: str) -> str:
    """
    Generate a contextually relevant response to a user query based on the provided document content using GPT-3.

    This function takes a list of relevant document chunks and a user query, constructs a prompt that includes
    the document content and query, and uses the OpenAI API to generate an answer. The response is based on
    the context provided by the document chunks.

    Args:
        relevant_chunks (list): A list of text chunks that are most relevant to the user's query, typically
                                 retrieved from the document's FAISS index.
        query (str): The user's question or query based on which the response is to be generated.

    Returns:
        str: The generated response from the AI model, based on the provided context and query.
    """
    context = "\n".join(relevant_chunks)
    prompt = f"Answer the following question based on the document content:\n\n{context}\n\nQuestion: {query}\nAnswer:"

    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )

    return response.choices[0].text.strip()
