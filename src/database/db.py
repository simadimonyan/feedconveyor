from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_milvus import Milvus
from dotenv import load_dotenv
import os

class Database:

    def __init__(self):
        load_dotenv(".env")
        server = os.getenv("MILVUS_HOST")
        name = os.getenv("MILVUS_USER")
        pwd = os.getenv("MILVUS_PASSWORD")
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        ollama_model = os.getenv("OLLAMA_MODEL")
        self.ollama = ChatOllama(model=ollama_model, base_url=ollama_url)
        embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)

        self.vector_store = Milvus(
            embedding_function=embeddings,
            connection_args={"uri": server},
            collection_name="store"
        )

    async def store_data(self, data):
        self.vector_store.aadd_documents(data)

    def search(self, search):
        pass

