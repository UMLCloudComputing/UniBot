import time
import os
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document  
import requests
import json
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Environmental Variables
def get_vector_index(index_name):
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    vector_store = PineconeVectorStore(index=index, embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
    return vector_store

def process_file(file_name):
    with open(f"dataset/{file_name}", "r") as file:
        data = json.load(file)
        return {
            "id": data["url"],
            "values": data["embedding"],
            "metadata": {
                "url": data["url"],
                "text": data["text"]
            }
        }

def import_documents(index, numAtOnce):
    index = pc.Index(index)

    # Get all the files in the dataset folder
    files = os.listdir("data/dataset")
    print(files)

    vectors = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file_name) for file_name in files]
        for future in concurrent.futures.as_completed(futures):
            vectors.append(future.result())

    # wait for futures to complete
    concurrent.futures.wait(futures)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(index.upsert, vectors[i:i+numAtOnce]) for i in range(0, len(vectors), numAtOnce)]

def insert_document(index, content, url):
    index = pc.Index(index)

    # Set up the headers and data payload
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    data = {"input": content, "model": "text-embedding-3-small"}

    # Request Embeddings from OpenAI
    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data)
    embed_array = response.json()["data"]

    # Convert URL to a filesystem safe name
    filesystem_url = [url.replace("/", "_") for url in url]


    vectors = []
    for text in content:
        for embed in embed_array:
            for urls in url:
                vectors.append({"id": urls, "values": embed["embedding"], "metadata": {"url": urls, "text": text}})
                # Save the embed in a CSV file in dataset/

                # Create dataset folder if it doesn't exist
                newpath = "dataset"
                if not os.path.exists(newpath):
                    os.makedirs(newpath)

                with open(f"data/dataset/{urls.replace('/', '_')}.json", "w") as file:
                    data = {
                        "url": urls,
                        "embedding": embed["embedding"],
                        "text": text
                    }
                    json.dump(data, file, indent=4)


    index.upsert(vectors)

def delete_document(vector, url):
    vector.delete_documents(ids=[url])