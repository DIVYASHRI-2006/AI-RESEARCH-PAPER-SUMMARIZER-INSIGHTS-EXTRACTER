import streamlit as st

st.set_page_config(layout="wide")

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from llm_handler import ask_llm

from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import io

# ---------------- 🌌 ULTRA DARK CYAN UI ----------------
st.markdown("""
<style>

/* 🌌 Background */
html, body, [class*="css"] {
    background: linear-gradient(135deg, #05080f, #0e1117);
    color: #e0f7ff;
    font-family: 'Segoe UI', sans-serif;
}

/* ✨ Title */
h1 {
    color: #00ffff;
    font-weight: 800;
    text-shadow: 0px 0px 10px #00ffff;
}

/* 🔹 Subheaders */
h2, h3 {
    color: #00e5ff;
}

/* 🔍 Input */
.stTextInput input {
    background-color: #121826;
    color: #e0f7ff;
    border-radius: 14px;
    border: 2px solid #00ffff;
    padding: 12px;
    transition: 0.3s;
}

.stTextInput input:focus {
    border: 2px solid #00e5ff;
    box-shadow: 0 0 10px #00ffff;
}

/* 🚀 Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00ffff, #00c3ff);
    color: black;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #00e5ff, #0099ff);
    color: white;
    transform: scale(1.05);
}

/* 📑 Tabs */
.stTabs [role="tab"] {
    background-color: #121826;
    color: #ccefff;
    border-radius: 12px;
    padding: 12px;
    margin-right: 5px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #00ffff, #00c3ff);
    color: black;
    font-weight: bold;
}

/* 📊 Metrics */
[data-testid="metric-container"] {
    background: #121826;
    border: 1px solid #00ffff;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 0px 10px rgba(0,255,255,0.2);
}

/* 📋 Dataframe */
.stDataFrame {
    background-color: #121826;
    border-radius: 10px;
}

/* 📂 Expander */
.streamlit-expanderHeader {
    background-color: #121826;
    color: #00ffff;
    border-radius: 10px;
}

/* ⬇ Download */
.stDownloadButton>button {
    background: linear-gradient(90deg, #00ffff, #00ff9d);
    color: black;
    font-weight: bold;
    border-radius: 12px;
}

/* ⚠ Warning */
.stAlert {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- 🌟 TITLE ----------------
st.markdown(
    "<h1 style='text-align:center;'>🚀 AI-Powered Research Paper Summarizer & Insight Extractor</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; color:#8fdfff;'>🔍 Ask questions & extract intelligent insights from research papers</p>",
    unsafe_allow_html=True
)
paper_titles = []
# ---------------- 📑 TABS ----------------
tab1, tab2 = st.tabs(['📄 Research Paper QA', "🧠 Knowledge Graph Explorer"])

# ---------------- 📄 TAB 1 ----------------
with tab1:

    @st.cache_resource
    def load_vector_db():
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_db = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_db

    vector_db = load_vector_db()

    st.write("📚 **Total Papers in Database:**", vector_db.index.ntotal)

    user_query = st.text_input("🔎 Ask a question about research papers:")

    if st.button("🚀 Search Insights"):

        results = vector_db.similarity_search(user_query, k=3)

        content = ""

        for idx, doc in enumerate(results, 1):
            title = doc.metadata.get("title", f"Paper {idx}")
            content += f"""
            Paper Title: {title}

            Paper Content:
            {doc.page_content}
            """

        with st.spinner("🤖 AI is analyzing research papers..."):
           response = ask_llm(content, user_query)

        answer = ""
        paper_titles = []

        if "Research Paper:" in response:
            parts = response.split("Research Paper:")
            answer = parts[0].replace("Answer:", "").strip()
            papers_text = parts[1].strip()
            paper_titles = [p.strip() for p in papers_text.split(",")]
        else:
            answer = response.strip()

        st.subheader("🤖 AI Generated Insight")
        st.success(answer)

        if paper_titles and "none" not in [p.lower() for p in paper_titles]:
            st.subheader("📄 Relevant Research Papers")

            found = False

if paper_titles and "none" not in [p.lower() for p in paper_titles]:

    for doc in results:
        title = doc.metadata.get("title", "")

        for p in paper_titles:
            if p.lower() in title.lower():
                found = True
                with st.expander(f"📄 {title}"):
                    st.write(doc.page_content)

# 🔥 Fallback
if not found:
    st.warning("⚠ Showing top similar papers (AI matching fallback) 👇")

    for doc in results:
        title = doc.metadata.get("title", "Untitled")
        with st.expander(f"📄 {title}"):
            st.write(doc.page_content[:500])

# ---------------- 🧠 TAB 2 ----------------
with tab2:

    st.subheader("🧠 Knowledge Graph Explorer")

    @st.cache_resource
    def get_driver():
        return GraphDatabase.driver(
            "neo4j://127.0.0.1:7687",
            auth=('neo4j','SSDP7676')
        )

    driver = get_driver()

    @st.cache_data
    def get_domain():
        query = """ 
        MATCH (d:Domain)
        RETURN d.name as domain
        """
        with driver.session() as session:
            result = session.run(query)
            domains = [r["domain"] for r in result]

        normalized = {}
        for d in domains:
            normalized[d.lower()] = d.title()

        return sorted(normalized.values())

    domain = st.selectbox("📚 Select Research Domain", get_domain())

    def get_graph_data(domain):
        query = """ 
        MATCH (p:Paper)-[:BELONGS_TO]->(d:Domain)
        WHERE toLower(d.name) = toLower($domain)

        OPTIONAL MATCH (p)<-[:WROTE]-(a:Author)
        OPTIONAL MATCH (p)-[:USES]-(m:Method)

        RETURN p.title AS paper,
        a.name AS author,
        m.name AS method,
        d.name AS domain
        """
        with driver.session() as session:
            result = session.run(query, domain=domain)
            return [r.data() for r in result]

    def draw_graph(data):

        net = Network(
            height="600px",
            width="100%",
            bgcolor="#05080f",
            font_color="white"
        )

        for row in data:
            paper = row['paper']
            author = row['author']
            method = row['method']
            domain = row['domain']

            net.add_node(paper, label=paper, color="#00ffff")

            if author:
                net.add_node(author, label=author, color="#03a9f4")
                net.add_edge(author, paper)

            if method:
                net.add_node(method, label=method, color="#00ff9d")
                net.add_edge(paper, method)

            if domain:
                net.add_node(domain, label=domain, color="#9c27b0")
                net.add_edge(paper, domain)

        net.save_graph("graph.html")

        with open("graph.html", 'r', encoding='utf-8') as f:
            components.html(f.read(), height=600)

    if domain:

        st.subheader(f"📊 Knowledge Graph for Domain: {domain}")

        data = get_graph_data(domain)

        if len(data) == 0:
            st.warning("⚠ No papers found")

        else:
            df = pd.DataFrame(data)

            papers = df['paper'].nunique()
            authors = df['author'].nunique()
            methods = df['method'].nunique()

            col1, col2, col3 = st.columns(3)

            col1.metric("📄 Papers", papers)
            col2.metric("👨‍💻 Authors", authors)
            col3.metric("⚙ Methods", methods)

            st.divider()

            st.subheader("📋 Filtered Research Data")
            st.dataframe(df, use_container_width=True)

            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)

            st.download_button(
                "⬇ Export Excel",
                excel_buffer,
                file_name=f"{domain}_research_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.divider()

            st.subheader("🌐 Knowledge Graph Visualization")
            draw_graph(data)