# pinecone_utils.py
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# Initialize Pinecone instance
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def insert_to_pinecone(id, text, embedding):
    try:
        # Storing the interaction with unique ID and embedding
        index.upsert([(id, embedding, {"text": text})])
        print(f"Inserted {id} into Pinecone.")
    except Exception as e:
        print(f"Error inserting into Pinecone: {e}")

def query_pinecone(embedding, top_k=1):
    try:
        # Querying for the most relevant previous interactions
        results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
        return results
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return None
