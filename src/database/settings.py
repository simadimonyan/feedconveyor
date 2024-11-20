from pymilvus import MilvusClient
from dotenv import load_dotenv
import os

# update Milvus root default password as an external image 

def main():

    load_dotenv(".env")
    server = os.getenv("MILVUS_HOST")
    pwd = os.getenv("MILVUS_PASSWORD")

    client = MilvusClient(
        uri=server, 
        user="root", # Default username
        password="Milvus", # Default password
        timeout=2 # seconds
    ) 
    client.update_password( 
        user_name="root",  
        old_password="Milvus", 
        new_password=pwd
    )

if __name__ == "__main__":
    main()