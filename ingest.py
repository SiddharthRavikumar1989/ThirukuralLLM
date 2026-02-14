import pandas as pd
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    # 1. Load data
    data_path = os.path.join(os.path.dirname(__file__), "thirukural_data.csv")
    df = pd.read_csv(data_path)
    
    # 2. Prepare documents for indexing
    documents = []
    for _, row in df.iterrows():
        # Combine Tamil and English for bilingual embedding
        # We use a separator that the model can understand
        kural_tamil = str(row['Kural']).replace('<br />', ' ').strip()
        kural_english = str(row['Couplet']).strip()
        
        # This is the "content" that will be converted to vectors
        page_content = f"Tamil: {kural_tamil}\nEnglish: {kural_english}"
        
        # Prepare metadata for filtering and detailed lookup
        metadata = {
            "id": int(row['ID']),
            "tamil_kural": kural_tamil,
            "english_kural": kural_english,
            "adhigaram": str(row['Adhigaram']),
            "paal": str(row['Paal']),
            "iyal": str(row['Iyal']),
            "meaning_tamil": str(row['M_Varadharajanar']),
            "meaning_english": str(row.get('Meaning', row['Couplet'])) # Fallback if 'Meaning' column name is different
        }
        
        documents.append(Document(page_content=page_content, metadata=metadata))
    
    # 3. Initialize Embeddings and Chroma
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
    
    print(f"Ingesting {len(documents)} Kurals into ChromaDB...")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Ingestion complete. Database persisted at:", persist_directory)

if __name__ == "__main__":
    ingest_data()
