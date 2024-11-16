from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from dotenv import load_dotenv
import chromadb
import os

class Database:

    def __init__(self):
        load_dotenv(".env")
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        ollama_model = os.getenv("OLLAMA_MODEL")
        self.ollama = ChatOllama(model=ollama_model, base_url=ollama_url)
        self.embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)
        ef = OllamaEmbeddingFunction(
            model_name=ollama_model,
            url=ollama_model,
        )

        self.client = chromadb.HttpClient(host="chromadb", port=8000)
        self.collection = self.client.get_or_create_collection(name="store", embedding_function=ef)

    async def store_data(self, data, metadatas, ids):
        await self.collection.add(ids=ids, documents=data, metadatas=metadatas)

    async def search(self, search):
        return await self.collection.query(search)


