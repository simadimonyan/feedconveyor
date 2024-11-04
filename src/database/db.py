import json
from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector

class Database:

    def __init__(self) -> None:
        connection = "postgresql+psycopg://admin:admin@postgresql-pgvector:5432/feedconveyor" 
        embeddings = OllamaEmbeddings(model="llama3")

        self.vector_database = PGVector(
            collection_name="store",
            connection=connection,
            embeddings=embeddings,
        )
        self.vector_database.create_vector_extension()
        self.vector_database.create_tables_if_not_exists()

    def store_data(self, data):
        self.vector_database.add_documents(data, ids=[doc.metadata["id"] for doc in data])
