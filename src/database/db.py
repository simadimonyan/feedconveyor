from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from dotenv import load_dotenv
import chromadb
import os

class Database:

    def __init__(self):
        load_dotenv(".env")
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        ollama_model = os.getenv("OLLAMA_MODEL")
        self.ollama = ChatOllama(model=ollama_model, base_url=ollama_url)
        embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)

        #TODO make direct connection as a client 

        self.vector_store = Chroma(
            client=persistent_client,
            collection_name=collection.name,
            embedding_function=embeddings
        )

    def store_data(self, data, ids):
        self.vector_store.add_documents(documents=data, ids=ids)

    async def search(self, search):
        docs = await self.vector_store.asimilarity_search(search)
        return docs


