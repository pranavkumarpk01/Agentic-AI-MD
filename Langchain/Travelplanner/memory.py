from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

def save_memory(user_message, ai_response):

    text = f"""
USER: {user_message}

AI: {ai_response}
"""

    vector_db.add_texts([text])


def retrieve_memory(query, k=5):

    docs = vector_db.similarity_search(
        query=query,
        k=k
    )

    if not docs:
        return ""

    return "\n".join(
        [doc.page_content for doc in docs]
    )