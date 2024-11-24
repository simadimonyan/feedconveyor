from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient
import os

class Database:

    def __init__(self):
        load_dotenv(".env")
        server = os.getenv("MILVUS_HOST")
        pwd = os.getenv("MILVUS_PASSWORD")
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        ollama_model = os.getenv("OLLAMA_MODEL")
        self.ollama = ChatOllama(model=ollama_model, base_url=ollama_url)
        self.embeddings = OllamaEmbeddings(model=ollama_model, base_url=ollama_url)

        self.client = MilvusClient(
            uri=server,
            db_name="default",
            user="root",
            password=pwd
        )

        if not self.client.has_collection(collection_name="store"):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary key"),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=4096, description="Ollama embeddings"),  
                FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=1000, description="Document date"),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1000, description="Document title"),
                FieldSchema(name="source_link", dtype=DataType.VARCHAR, max_length=1000, description="Document link"),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, description="Original document content")
            ]
            schema = CollectionSchema(fields, description="LangChain-compatible Milvus collection for Ollama embeddings")

            self.client.create_collection(collection_name="store", schema=schema)

            index_params = MilvusClient.prepare_index_params()

            index_params.add_index(
                field_name="vector",
                metric_type="COSINE",
                index_type="IVF_FLAT",
                index_name="vector_index",
                params={ "nlist": 128 }
            )

            self.client.create_index(
                collection_name="store",
                index_params=index_params,
                sync=False 
            )
        
        self.client.load_collection("store")

    async def store_data(self, data):
        content = f"date: {data["date"]}, title: {data["title"]}, \
              source_link: {data["source_link"]}, text: {data["text"]}"
        vector = self.embeddings.embed_query(content)
        self.client.insert(
            collection_name="store",
            data={"vector": vector, "date": str(data["date"]), "title": str(data["title"]), \
                   "source_link": str(data["source_link"]), "text": str(data["text"])}
        )

    def search(self, search):
        return self.client.search(
            collection_name="store",
            data=[self.embeddings.embed_query(search)],
            limit=3,
            output_fields=["date", "title", "source_link", "text"]
        )

