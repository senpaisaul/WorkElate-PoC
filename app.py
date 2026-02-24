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

# --- Page Configuration ---
st.set_page_config(page_title="WorkElate OS", page_icon="🧠", layout="wide")

# --- Premium CSS Styling ---
st.markdown("""
    <style>
    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1a1c2c, #0e1117);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 33, 48, 0.5);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }

    /* Glassmorphism Card for AI Responses */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        color: white;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin: 20px 0;
    }

    /* Glowing Headers */
    .glow-header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        letter-spacing: -2px;
    }

    /* Action Button Glow */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #0080ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
        font-weight: bold;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        transform: translateY(-2px);
    }

    /* Subtitle Styling */
    .subtitle {
        color: #8a8d97;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize AI (Cached for Performance) ---
@st.cache_resource
def init_ai():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(index_name="workelate-v1-index", embedding=embeddings)
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    return vectorstore, llm

vectorstore, llm = init_ai()

# --- Custom Header Layout ---
col_head1, col_head2 = st.columns([1, 6])
with col_head1:
    # Reliable CDN Logo for a tech/brain icon
    st.image("https://cdn-icons-png.flaticon.com/512/6530/6530181.png", width=100)
with col_head2:
    st.markdown("<h1 class='glow-header'>WorkElate OS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>One-Brain Workspace | LPU-Inference Project Orchestration</p>", unsafe_allow_html=True)

st.divider()

# --- Sidebar Logic ---
with st.sidebar:
    st.markdown("### 🔐 Identity Selection")
    mode = st.radio("Access Level", ["🏢 Client Portal", "👨‍💻 Developer Hub"], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("🔒 End-to-End Encrypted Metadata Filter Active")

# --- 1. DEVELOPER HUB ---
if mode == "👨‍💻 Developer Hub":
    st.subheader("Update Project Velocity")
    dev_id = st.text_input("Developer ID:", placeholder="Enter D-Series Key...")
    
    if dev_id:
        with open("data.json", "r") as f:
            db = json.load(f)
        assigned = [p for p in db if p["developer_id"] == dev_id]
        
        if assigned:
            project = st.selectbox("Current Active Sprint", assigned, format_func=lambda x: f"{x['client_name']} ({x['customer_id']})")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                update_text = st.text_area("Log Daily Progress", placeholder="What milestones were reached today?", height=150)
            with c2:
                st.info("💡 Pro-tip: Specific updates (dates, ticket IDs) improve AI recall for the client.")
            
            if st.button("🚀 Push to Living Inbox"):
                if update_text:
                    new_doc = Document(
                        page_content=f"NEW UPDATE [{datetime.now().strftime('%Y-%m-%d %H:%M')}]: {update_text}",
                        metadata={"customer_id": project['customer_id']}
                    )
                    vectorstore.add_documents([new_doc])
                    st.success("Synchronized across the One-Brain Workspace.")
                    st.balloons()
        else:
            st.error("Access Key Denied.")

# --- 2. CLIENT PORTAL ---
else:
    st.subheader("Client Project Dashboard")
    client_id = st.sidebar.text_input("Enter Access Key (Client ID):", type="password")

    if client_id:
        with open("data.json", "r") as f:
            db = json.load(f)
        client_data = next((c for c in db if c["customer_id"] == client_id), None)
        
        if client_data:
            st.markdown(f"#### 👋 Welcome back, {client_data['client_name']}")
            
            # Interactive Query Area
            query = st.text_input("How can I help you with your project today?", placeholder="e.g., 'What is the status of the AWS migration?'")

            if query:
                with st.spinner("🧠 Orchestrating Workspace context..."):
                    # We pull top 5 chunks to ensure history + latest update are found
                    docs = vectorstore.similarity_search(query, k=5, filter={"customer_id": client_id})
                    context = "\n\n---\n\n".join([d.page_content for d in docs])
                    
                    prompt = ChatPromptTemplate.from_template("""
                    Role: Professional WorkElate Assistant.
                    Context: {c}
                    Q: {q}
                    Focus on the most recent updates if available.
                    """)
                    chain = prompt | llm | StrOutputParser()
                    response = chain.invoke({"c": context, "q": query})

                    # Render response in the Premium Glass Card
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="color:#00d4ff; margin-top:0;">🤖 Assistant Intelligence</h3>
                            <p style="line-height:1.6; font-size:1.1rem;">{response}</p>
                            <hr style="opacity:0.1">
                            <small style="color:#8a8d97;">Source: Project-Filtered Vector Memory (k=5)</small>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Key verification failed.")
    else:
        # Styled helper for empty state
        st.markdown("""
            <div style="background: rgba(0, 212, 255, 0.05); padding: 2rem; border-radius: 15px; border: 1px dashed #00d4ff;">
                <p style="text-align: center; color: #00d4ff; margin: 0;">
                    🔑 Please provide your Secure Client ID in the sidebar to authenticate.
                </p>
            </div>
        """, unsafe_allow_html=True)