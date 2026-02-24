import json
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

INDEX_NAME = "workelate-v1-index"
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

if INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
    pc.create_index(name=INDEX_NAME, dimension=1536, metric="cosine", 
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"))

with open("data.json", "r") as f:
    data = json.load(f)

docs = []
for item in data:
    # We combine all fields into the content so the AI can answer any question
    content = f"Client: {item['client_name']}. Details: {item['project_details']} Milestones: {item['milestones']} Security/Budget: {item.get('security') or item.get('budget')}"
    docs.append(Document(page_content=content, metadata={"customer_id": item['customer_id']}))

vectorstore = PineconeVectorStore.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"), index_name=INDEX_NAME)
print("✅ Second Brain refreshed with granular metadata.")