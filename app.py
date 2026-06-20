import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

@st.cache_resource
def load_models():
    chroma_client = chromadb.PersistentClient(path="storage/chromadb")
    collection = chroma_client.get_collection("lufthansa_intelligence")
    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2",
        token=os.getenv("HF_TOKEN")
    )
    return collection, model

live_collection, live_model = load_models()


def live_search_and_recommend(question):
    # Step 1: Retrieve - semantic search in ChromaDB
    query_embedding = live_model.encode([question]).tolist()
    results = live_collection.query(query_embeddings=query_embedding, n_results=5)

    docs_text = ""
    for metadata, text in zip(results["metadatas"][0], results["documents"][0]):
        docs_text += f"- {metadata['title']}: {text}\n\n"

    # Step 2: Generate - send retrieved docs to LLM
    prompt = f"""You are a strategic analyst for Lufthansa Group.

Question: {question}

Relevant documents (some may be in German, respond in English):
{docs_text}

Provide a clear, evidence-based answer with a specific recommendation."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi4-mini", "prompt": prompt, "stream": False}
    )

    return response.json()["response"], results["metadatas"][0]
# ── Lufthansa Brand Styling ──────────────────────────
# ── Lufthansa Brand Styling ──────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }

    /* Top navy bar effect on the title area */
    .main .block-container {
        padding-top: 1rem;
    }

    h1, h2, h3, h4 {
        color: #0A1A4F !important;
    }

    p, .stMarkdown, .stCaption, label {
        color: #1A1A1A;
    }

    .stButton button {
    background-color: #0A1A4F;
    color: #FFFFFF !important;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    }

    .stButton button:hover {
    background-color: #FFC600;
    color: #0A1A4F !important;
    }

    .stButton button p {
    color: #FFFFFF !important;
    }

    .stButton button:hover p {
    color: #0A1A4F !important;
    }

    .stTextInput input {
    border: 1px solid #0A1A4F;
    color: #0A1A4F !important;
    background-color: #FFFFFF !important;
    }

    [data-testid="stExpander"] summary {
    background-color: #0A1A4F !important;
    border-radius: 4px;
    }

    [data-testid="stExpander"] summary p {
        color: #FFFFFF !important;
    }

    [data-testid="stExpander"] summary span {
        color: #FFFFFF !important;
    }

    .stExpander {
        border: 1px solid #E0E0E0;
        background-color: #F8F9FB;
    }

    hr {
        border-color: #0A1A4F;
    }
</style>
""", unsafe_allow_html=True)
# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    # page_title="Lufthansa Strategic Intelligence",
    page_icon="✈️",
    layout="wide"
)

# ── Title ──────────────────────────
st.title("✈️ Lufthansa Group — Executive Intelligence Dashboard")
st.markdown("AI-powered strategic intelligence for executive decision-making")

st.image("assets/lufthansaannounces1_1776846116 (1).jpg", use_container_width=True)

st.divider()
# ── Load all data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    import chromadb
    chroma_client = chromadb.PersistentClient(path="storage/chromadb")
    collection = chroma_client.get_collection("lufthansa_intelligence")
    data = collection.get()

    documents = []
    for i in range(len(data["ids"])):
        documents.append({
            "title": data["metadatas"][i]["title"],
            "summary": data["documents"][i],
            "category": data["metadatas"][i]["category"],
            "source": data["metadatas"][i]["source"],
            "date": data["metadatas"][i]["date"]
        })

    with open("data/intelligence_results.json") as f:
        intelligence = json.load(f)
    with open("data/sentiment_results.json") as f:
        sentiment = json.load(f)
    with open("data/evidence_based_recommendations.json") as f:
        recommendations = json.load(f)
    with open("data/ceo_recommendation.txt") as f:
        ceo_briefing = f.read()
    return documents, intelligence, sentiment, recommendations, ceo_briefing

documents, intelligence, sentiment, recommendations, ceo_briefing = load_data()


# ── Section 1: Company Overview ───────────────────────────────
st.header("📊 Company Overview")

sources = list(set(d["source"] for d in documents))

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Company", "Lufthansa AG")
col2.metric("Industry", "Aviation")
col3.metric("Documents Collected", len(documents))
col4.metric("Data Sources", len(sources))
col5.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))
st.divider()

# ── Section 2: Market Intelligence ───────────────────────────
st.header("Market Intelligence")

tab1, tab2, tab3 = st.tabs(["Recent News", "Competitor Activity", "Company Announcements"])

with tab1:
    news_docs = [d for d in documents if d["category"] == "news"][:10]
    for doc in news_docs:
        st.markdown(f"**{doc['title']}**")
        st.caption(f"{doc['source']} — {doc['date']}")
        st.write(doc["summary"][:200])
        st.divider()

with tab2:
    market_docs = [d for d in documents if d["category"] == "market"][:10]
    for doc in market_docs:
        st.markdown(f"**{doc['title']}**")
        st.caption(f"{doc['source']} — {doc['date']}")
        st.write(doc["summary"][:200])
        st.divider()

with tab3:
    company_docs = [d for d in documents if d["category"] == "company"][:10]
    for doc in company_docs:
        st.markdown(f"**{doc['title']}**")
        st.caption(f"{doc['source']} — {doc['date']}")
        st.write(doc["summary"][:200])
        st.divider()

st.divider()

# ── Section 3: Opportunity Monitor ───────────────────────────
st.header("Opportunity Monitor")

for opp in intelligence["opportunities"]:
    with st.expander(f"🟢 {opp['title']} — Impact: {opp['impact']}"):
        st.write(opp["description"])
        st.caption(f"Evidence: {opp['evidence']}")
        st.caption(f"Confidence: {opp['confidence_score']}/10")

st.divider()

# ── Section 4: Risk Monitor ───────────────────────────────────
st.header("Risk Monitor")

for risk in intelligence["risks"]:
    with st.expander(f"🔴 {risk['title']} — Severity: {risk['severity']}"):
        st.write(risk["description"])
        st.caption(f"Evidence: {risk['evidence']}")
        st.caption(f"Confidence: {risk['confidence_score']}/10")

st.divider()

# ── Section 5: Sentiment Analysis ────────────────────────────
# ── Section 5: Sentiment Analysis ────────────────────────────
st.header("💬 Section 5: Sentiment Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("News vs Public Sentiment")
    plt.style.use("dark_background")
    labels = ["Positive", "Negative", "Neutral"]
    news_vals = [sentiment["news_sentiment"][l.lower()] for l in labels]
    public_vals = [sentiment["public_sentiment"][l.lower()] for l in labels]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    x = range(len(labels))
    ax.bar([i - 0.2 for i in x], news_vals, width=0.4, label="News", color="#4FC3F7")
    ax.bar([i + 0.2 for i in x], public_vals, width=0.4, label="Public", color="#FFA726")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend(frameon=False)
    ax.set_title("Sentiment Comparison", fontsize=13, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("Sentiment Trends by Month")
    trends = sentiment["sentiment_trends"]
    sorted_months = sorted(trends.keys())
    pos = [trends[m]["positive"] for m in sorted_months]
    neg = [trends[m]["negative"] for m in sorted_months]
    neu = [trends[m]["neutral"] for m in sorted_months]

    fig2, ax2 = plt.subplots(figsize=(6, 4.5))
    ax2.plot(sorted_months, pos, label="Positive", color="#66BB6A", linewidth=2)
    ax2.plot(sorted_months, neg, label="Negative", color="#EF5350", linewidth=2)
    ax2.plot(sorted_months, neu, label="Neutral", color="#BDBDBD", linewidth=2)
    step = max(1, len(sorted_months)//6)
    ax2.set_xticks(range(0, len(sorted_months), step))
    ax2.set_xticklabels(sorted_months[::step], rotation=45)
    ax2.legend(frameon=False)
    ax2.set_title("Sentiment Trend", fontsize=13, fontweight="bold")
    ax2.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)

st.subheader("Overall Sentiment Share")

total_pos = sum(trends[m]["positive"] for m in trends)
total_neg = sum(trends[m]["negative"] for m in trends)
total_neu = sum(trends[m]["neutral"] for m in trends)

df_pie = pd.DataFrame({
    "Sentiment": ["Positive", "Neutral", "Negative"],
    "Count": [total_pos, total_neu, total_neg]
})

fig_pie = px.pie(
    df_pie, values="Count", names="Sentiment", hole=0.5,
    color="Sentiment",
    color_discrete_map={"Positive": "#2ECC71", "Neutral": "#95A5A6", "Negative": "#E74C3C"}
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ── Section 6: Strategic Recommendations ─────────────────────
st.header("Strategic Recommendations")

for i, rec in enumerate(recommendations["recommendations"], 1):
    with st.expander(f"Recommendation {i}: {rec['recommendation'][:80]}"):
        st.write(f"**Recommendation:** {rec['recommendation']}")
        st.write("**Supporting Evidence:**")
        for ev in rec["supporting_evidence"]:
            st.write(f"  - {ev}")
        st.write("**Expected Impact:**")
        for k, v in rec["expected_impact"].items():
            st.write(f"  - {k.replace('_', ' ').title()}: {v}")
        st.write("**Risk Assessment:**")
        for k, v in rec["risk_assessment"].items():
            st.write(f"  - {k.replace('_', ' ').title()}: {v}")

st.divider()

# ── Section 7: CEO Briefing ───────────────────────────────────
st.header("CEO Briefing")
st.info("AI-generated executive summary based on live intelligence analysis")
st.write(ceo_briefing)
st.divider()
st.header("🔍 Live Strategic Query")
st.markdown("Ask the Strategic Intelligence Agent a question — it will retrieve relevant documents live and generate a fresh, evidence-based answer.")

user_question = st.text_input("Ask a question (e.g. 'What are Lufthansa's biggest risks right now?')")

if st.button("Ask the Agent"):
    if user_question:
        with st.spinner("Retrieving relevant documents and generating analysis..."):
            answer, evidence = live_search_and_recommend(user_question)

        st.subheader("Answer")
        st.write(answer)

        st.subheader("Evidence Used")
        for doc in evidence:
            st.caption(f"- {doc['title']} ({doc['source']})")
    else:
        st.warning("Please type a question first.")

st.divider()
