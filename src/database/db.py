from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_postgres import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import json

class Database:

    def __init__(self):
        load_dotenv(".env")
        name = os.getenv("POSTGRES_NAME")
        pwd = os.getenv("POSTGRES_PASSWORD")
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        ollama_model = os.getenv("OLLAMA_MODEL")
        self.ollama = ChatOllama(model=ollama_model, base_url=ollama_url)

        connection = f"postgresql+psycopg://{name}:{pwd}@postgresql-pgvector:5432/feedconveyor" 
        embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)
        
        self.vector_database = PGVector(
            collection_name="store",
            connection=connection,
            embeddings=embeddings
        )
        self.vector_database.create_vector_extension()
        self.vector_database.create_tables_if_not_exists()


    async def store_data(self, data):

        for doc in data:
            if not isinstance(doc.metadata, dict):
                raise ValueError("Metadata must be a dictionary")
        
        self.vector_database.add_documents(data, ids=[doc.metadata["id"] for doc in data])

    def search(self, search):
        docs: dict[Document] = self.vector_database.similarity_search(search)

        for doc in docs:
            if not isinstance(doc.metadata, dict):
                raise ValueError("Retrieved metadata must be a dictionary")

        return docs


