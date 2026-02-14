import os
import random
import pandas as pd
from dotenv import load_dotenv

# Load .env from the same directory as this script FIRST
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from typing import List

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "thirukural_data.csv")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Lazy initialization of vectorstore
_vectorstore = None

from ingest import ingest_data
import shutil

def get_vectorstore():
    global _vectorstore
    
    # Check if vectorstore exists
    if not os.path.exists(DB_DIR) or not os.listdir(DB_DIR):
        print("Vectorstore not found. Building fresh index...")
        ingest_data()
        
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        _vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return _vectorstore

@tool
def search_kurals(query: str) -> str:
    """Semantic search to find top 5 related Kurals based on a word or context. 
    Input can be in Tamil or English."""
    vs = get_vectorstore()
    results = vs.similarity_search(query, k=5)
    
    output = "Top 5 Related Kurals:\n\n"
    for i, res in enumerate(results):
        m = res.metadata
        output += f"{i+1}. ID: {m['id']} | Category: {m['paal']}\n"
        output += f"Tamil: {m['tamil_kural']}\n"
        output += f"English: {m['english_kural']}\n\n"
    return output

@tool
def get_kural_explanation(kural_id: int) -> str:
    """Provides a detailed explanation for a specific Kural ID in both Tamil and English."""
    vs = get_vectorstore()
    results = vs.get(where={"id": kural_id})
    
    if not results['documents']:
        return f"Kural with ID {kural_id} not found."
    
    m = results['metadatas'][0]
    output = f"Explanation for Kural {kural_id}:\n\n"
    output += f"Tamil Kural: {m['tamil_kural']}\n"
    output += f"English Kural: {m['english_kural']}\n\n"
    output += f"Tamil Meaning (மு.வ): {m['meaning_tamil']}\n\n"
    output += f"English Meaning: {m['meaning_english']}\n"
    return output

@tool
def get_random_kural_by_category(category: str) -> str:
    """Pulls up a random Kural from a specific category (Paal). 
    Categories include: Arathuppaal (Virtue), Porutpaal (Wealth), Kaamathuppaal (Love)."""
    df = pd.read_csv(DATA_PATH)
    
    # Simple normalization for category matching
    cat_map = {
        "virtue": "Arathuppaal",
        "wealth": "Porutpaal",
        "love": "Kaamathuppaal",
        "அறத்துப்பால்": "Arathuppaal",
        "பொருட்பால்": "Porutpaal",
        "காமத்துப்பால்": "Kaamathuppaal"
    }
    
    target_cat = cat_map.get(category.lower(), category)
    filtered = df[df['Paal'] == target_cat]
    
    if filtered.empty:
        return f"No Kurals found for category: {category}. Try Arathuppaal, Porutpaal, or Kaamathuppaal."
    
    row = filtered.sample(n=1).iloc[0]
    kural_tamil = str(row['Kural']).replace('<br />', ' ').strip()
    
    output = f"Random Kural from {target_cat}:\n\n"
    output += f"ID: {row['ID']}\n"
    output += f"Tamil: {kural_tamil}\n"
    output += f"English: {row['Couplet']}\n"
    return output
