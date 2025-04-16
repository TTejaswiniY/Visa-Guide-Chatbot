from pinecone import Pinecone, ServerlessSpec
from embeddings import get_embedding
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("pcsk_6DZaGM_5nhMTK4SRnFUqFhqXzpaiL6VkwJRDhWCv9UJfWgevmkSHYntYUyxp8YTJy9ntss"))

index_name = "visa-guide-index"

# Create index if not exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Gemini embedding output dimension
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' already exists.")

# Connect to the index
index = pc.Index(index_name)

# Sample data (you can replace with chunked PDF content later)
documents = [
    {"id": "doc1", "text": "Tourist visas are typically valid for up to 6 months."},
    {"id": "doc2", "text": "Student visa applications must include a university admission letter."},
    {"id": "doc3", "text": "The B1/B2 visa allows business and tourism visits to the US."}
]

# Embed and upsert
for doc in documents:
    embedding = get_embedding(doc["text"])
    if embedding:
        index.upsert(vectors=[{
            "id": doc["id"],
            "values": embedding,
            "metadata": {"text": doc["text"]}
        }])
        print(f"Inserted {doc['id']} into index.")
    else:
        print(f"Skipping {doc['id']} due to embedding error.")
