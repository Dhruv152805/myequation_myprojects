"""
vector_store.py
---------------
WHAT IS CHROMADB?
  ChromaDB is a "vector database" — a special database built to store
  and search text embeddings (vectors).

  Normal SQL database search:  WHERE topic = 'boiler'
  ChromaDB search:             "find chunks SIMILAR IN MEANING to: how does a boiler work?"

HOW CHROMADB WORKS INTERNALLY:
  1. You insert text chunks + their embedding vectors
  2. ChromaDB builds an HNSW index (a fast approximate nearest-neighbor graph)
  3. When you search, it converts your query to a vector, then traverses
     the graph to find the K closest stored vectors in milliseconds
  4. It returns those chunks as your "context"

PERSISTENCE:
  We use persist_directory="./chroma_db" so the database is saved to disk.
  Next time you start the app, all previously indexed documents are still there.
  No need to re-upload and re-index every session!

COLLECTION:
  A ChromaDB "collection" is like a table in SQL.
  We use one collection called "industrial_docs" for all uploaded documents.
"""

import os
from langchain_community.vectorstores import Chroma
from chatbot.embeddings import get_embeddings

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "industrial_docs"


class VectorStoreManager:
    """
    Manages all ChromaDB operations:
    - Adding new document chunks
    - Semantic similarity search
    - Reporting how many chunks are indexed
    - Clearing the database
    """

    def __init__(self):
        self.embeddings = get_embeddings()
        # Connect to (or create) the persistent ChromaDB collection
        self.vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PATH,
        )

    def add_documents(self, chunks: list) -> int:
        """
        Embed and store document chunks.
        LangChain's Chroma.add_documents() does this automatically:
          chunk.page_content → embedding model → vector → stored in ChromaDB
        Returns the number of chunks added.
        """
        self.vectorstore.add_documents(chunks)
        return len(chunks)

    def get_retriever(self, k: int = 3):
        """
        Create a LangChain Retriever object.
        When queried, it:
          1. Embeds the question
          2. Finds top-K most similar chunks in ChromaDB
          3. Returns those chunks as LangChain Documents
        k=3 means we retrieve the 3 best matching chunks per question.
        """
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def get_chunk_count(self) -> int:
        """Return total number of stored chunks."""
        try:
            return self.vectorstore._collection.count()
        except Exception:
            return 0

    def clear_all(self):
        """Delete all documents from ChromaDB collection."""
        try:
            collection = self.vectorstore._collection
            existing = collection.get()
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
        except Exception as e:
            raise RuntimeError(f"Failed to clear database: {e}")

    def is_empty(self) -> bool:
        """Check if the database has any documents."""
        return self.get_chunk_count() == 0
