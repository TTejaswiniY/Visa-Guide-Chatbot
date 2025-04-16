import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from pinecone import Pinecone
from embeddings import get_embedding  # your working embedding function

load_dotenv()

# Load API keys and index name from .env
api_key = os.getenv("GOOGLE_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")
news_api_key = os.getenv("NEWS_API_KEY")  # Add your News API key here

# Check API key
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# Connect to Pinecone
pc = Pinecone(api_key=pinecone_key)
index = pc.Index(index_name)

# Function to retrieve visa-related news
def get_visa_news():
    url = f'https://newsapi.org/v2/everything?q=visa&apiKey={news_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        if articles:
            # Return the top 3 articles for now
            return "\n".join([f"{article['title']} - {article['url']}" for article in articles[:3]])
    return "No recent visa-related news found."

# Function to generate a visa checklist
def generate_visa_checklist(country):
    visa_checklists = {
        "US": ["Passport", "Visa application form", "Photographs", "Embassy appointment confirmation"],
        "Canada": ["Passport", "Proof of funds", "Visa application form", "Photographs"]
        # Add more countries and their checklist
    }
    return visa_checklists.get(country, "No checklist available for this country.")

# Function to get visa fees
def get_visa_fee(country):
    fees = {
        "US": "$160",
        "Canada": "$100"
        # Add more countries and their visa fees
    }
    return fees.get(country, "Fee information not available.")

# Function to handle long-term memory retrieval
def retrieve_context_from_pinecone(query_embedding):
    search_results = index.query(
        vector=query_embedding,
        top_k=3,  # Adjust top_k to retrieve more or fewer results
        include_metadata=True
    )
    contexts = [match["metadata"]["text"] for match in search_results.get("matches", [])]
    return "\n".join(contexts)

# Add a check for empty context and provide fallback response
def check_context(context_str, prompt):
    if not context_str:
        return f"Sorry, I don't have the information you're asking for. Can you clarify your question about '{prompt}'?"
    return None

print("🤖 Gemini Chatbot is ready! Type 'exit' to quit.")

while True:
    prompt = input("\nYou: ")
    if prompt.lower() == "exit":
        break

    # Step 1: Embed the query
    query_embedding = get_embedding(prompt)
    if not query_embedding:
        print("❌ Could not get embedding for query.")
        continue

    # Step 2: Retrieve context from Pinecone
    context_str = retrieve_context_from_pinecone(query_embedding)
    context_check = check_context(context_str, prompt)
    if context_check:
        print(context_check)
        continue

    # Step 3: Ask Gemini with context
    full_prompt = f"""Answer the question based on the context below. Be concise and clear in your response.

Context:
{context_str}

Question:
{prompt}

Provide a well-structured and detailed response. If the context doesn't contain the answer, say: 'I don't have the information regarding this.' 
"""
    try:
        response = model.generate_content(full_prompt)
        print("Gemini:", response.text)
    except Exception as e:
        print("❌ Error:", e)

    # Step 4: Retrieve real-time visa news (if the query is visa-related)
    if "visa" in prompt.lower():
        news = get_visa_news()
        print("Visa News:", news)

    # Step 5: Handle specific use-case tools (Visa checklist, fees)
    if "checklist" in prompt.lower():
        country = prompt.split()[-1]  # Assuming the country name is at the end of the sentence
        checklist = generate_visa_checklist(country)
        print(f"Visa Checklist for {country}: {checklist}")

    if "fee" in prompt.lower():
        country = prompt.split()[-1]  # Assuming the country name is at the end of the sentence
        fee = get_visa_fee(country)
        print(f"Visa Fee for {country}: {fee}")
