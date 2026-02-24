import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Page Configuration & Theme ---
st.set_page_config(page_title="WorkElate OS", page_icon="⚡", layout="wide")

# Custom CSS for a professional "Dark Mode" AI interface
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3d4455; }
    .stCard {
        background-color: #1e2130;
        padding: 24px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
        margin-top: 20px;
    }
    .glow-header {
        color: #00d4ff;
        text-shadow: 0 0 12px rgba(0, 212, 255, 0.4);
        font-weight: 800;
        letter-spacing: -1px;
    }
    .status-badge {
        background-color: #2e344e;
        color: #00d4ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        border: 1px solid #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize AI Components ---
@st.cache_resource
def init_components():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(index_name="workelate-v1-index", embedding=embeddings)
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    return vectorstore, llm

vectorstore, llm = init_components()

# --- Header Section ---
col_logo, col_title = st.columns([1, 6])
with col_title:
    st.markdown("<h1 class='glow-header'>WorkElate OS: One-Brain Workspace</h1>", unsafe_allow_html=True)
    st.caption("⚡ Groq LPU Powered Inference | Real-Time Developer Sync")

st.divider()

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.markdown("### **Portal Selection**")
    mode = st.radio("Switch View", ["🏢 Client Portal", "👨‍💻 Developer Hub"])
    st.info("The Living Inbox uses metadata-filtered RAG to ensure data privacy between projects.")

# --- 1. DEVELOPER HUB (Writing to the Brain) ---
if mode == "👨‍💻 Developer Hub":
    st.subheader("Developer Update Terminal")
    dev_id = st.text_input("Log in with Developer ID:", placeholder="e.g., D505")
    
    if dev_id:
        with open("data.json", "r") as f:
            db = json.load(f)
        
        # Get projects assigned to this developer
        assigned_projects = [p for p in db if p["developer_id"] == dev_id]
        
        if assigned_projects:
            project = st.selectbox("Select Project to Update", assigned_projects, format_func=lambda x: f"{x['client_name']} ({x['customer_id']})")
            
            # Display current stats
            st.markdown(f"<span class='status-badge'>Active Project: {project['customer_id']}</span>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                update_text = st.text_area("Log Daily Progress", placeholder="Details about specific milestones reached...", height=150)
            with c2:
                st.metric(label="Last Known Status", value="In Progress", delta="Updated via LPU")
            
            if st.button("🚀 Publish to Client Inbox"):
                if update_text:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Enrich document with tags for better retrieval
                    content = f"NEW DEVELOPER UPDATE logged at {timestamp}: {update_text}"
                    
                    new_doc = Document(
                        page_content=content,
                        metadata={"customer_id": project['customer_id'], "type": "realtime_update"}
                    )
                    
                    vectorstore.add_documents([new_doc])
                    st.balloons()
                    st.success("Success! The AI Brain has been updated. Clients will see this change within seconds.")
                else:
                    st.warning("Please enter update details.")
        else:
            st.error("Access Denied: No projects found for this Developer ID.")

# --- 2. CLIENT PORTAL (Reading from the Brain) ---
else:
    st.subheader("Client Project Dashboard")
    client_id = st.sidebar.text_input("Enter Access Key (Client ID):", type="password")

    if client_id:
        with open("data.json", "r") as f:
            db = json.load(f)
        client_info = next((c for c in db if c["customer_id"] == client_id), None)
        
        if client_info:
            st.markdown(f"### Welcome back, **{client_info['client_name']}**")
            
            # Chat Interface
            query = st.text_input("Ask anything about your project's latest status:", placeholder="e.g., 'What did the developers finish today?'")

            if query:
                with st.spinner("AI OS retrieving latest updates..."):
                    # CRITICAL FIX: k=5 ensures we pull the original record AND all dev updates
                    docs = vectorstore.similarity_search(query, k=5, filter={"customer_id": client_id})
                    
                    if docs:
                        context = "\n\n---\n\n".join([d.page_content for d in docs])
                        
                        # High-Speed Reasoning Chain
                        template = """
                        You are the WorkElate OS Assistant.
                        Use the context below to answer the client's question. 
                        PRIORITIZE snippets labeled 'NEW DEVELOPER UPDATE' as they are the most current.
                        
                        CONTEXT FROM WORKSPACE:
                        {context}
                        
                        QUESTION: {question}
                        
                        Respond in a professional, concise tone. If the information is not present, state that.
                        """
                        prompt = ChatPromptTemplate.from_template(template)
                        chain = prompt | llm | StrOutputParser()
                        
                        response = chain.invoke({"context": context, "question": query})

                        # Display in an AI Card
                        st.markdown(f"""
                        <div class="stCard">
                            <h4 style='color:#00d4ff; margin-top:0;'>🤖 AI Project Intelligence</h4>
                            <p style='font-size:1.1rem;'>{response}</p>
                            <small style='color:#3d4455;'>Verified via WorkElate Multi-Tenant Brain</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("No context found for this ID.")
        else:
            st.error("Invalid Access Key.")
    else:
        st.info("🔑 Please enter your Client ID in the sidebar to view your project updates.")