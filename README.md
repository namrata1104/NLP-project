# Lufthansa Strategic Intelligence Agent

An AI-powered Strategic Intelligence Agent built for Lufthansa Group. The system automatically collects live information about the company from the public web, stores and organizes it for semantic search, identifies opportunities, risks, and trends, and reasons like a CEO advisor to produce evidence-based strategic recommendations — all presented through an interactive executive dashboard.

The goal of this project is not information retrieval or summarization. The goal is **strategic decision-making**: the system is designed to answer the question *"If you were the CEO today, what would you do next and why?"*

---

## Table of Contents

- [Introduction](#introduction)
- [System Architecture Diagram](#system-architecture-diagram)
- [Data Flow Diagram](#data-flow-diagram)
- [Technology Stack](#technology-stack)
- [AI Pipeline](#ai-pipeline)
- [Design Decisions](#design-decisions)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)

---

## Introduction

Organizations today are surrounded by a continuous flow of information — news, financial reports, competitor activity, customer feedback, and industry trends. The challenge is no longer *finding* information; it is *transforming* it into strategic decisions.

This project builds an AI Strategic Intelligence Agent for **Lufthansa Group** that:

1. **Collects** live, real information about Lufthansa from multiple independent public sources, in both English and German
2. **Stores** that information in a searchable knowledge repository
3. **Cleans and filters** the data to keep only relevant, deduplicated content
4. **Identifies** opportunities, risks, and trends using Retrieval-Augmented Generation (RAG)
5. **Reasons** like a CEO advisor — prioritizing actions, justifying decisions, and explicitly addressing trade-offs
6. **Produces** evidence-based recommendations with expected impact and risk assessment
7. **Analyzes sentiment** across news and public/community sources
8. **Presents** everything through an interactive Streamlit dashboard, including a live query feature

---

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph Collection["Data Collection Layer"]
        A1[DuckDuckGo Search]
        A2[Wikipedia EN + DE]
        A3[Google News RSS]
        A4[Reddit RSS]
    end

    subgraph Processing["Processing Layer"]
        B1[Clean Text]
        B2[Deduplicate]
        B3[Filter for Relevance]
        B4[Generate Embeddings]
    end

    subgraph Storage["Knowledge Repository"]
        C1[(ChromaDB<br/>Vector Store)]
    end

    subgraph Intelligence["Intelligence Layer"]
        D1[Semantic Search /<br/>Retrieval]
        D2[Strategic Intelligence Engine<br/>Opportunities · Risks · Trends]
        D3[AI CEO Agent<br/>Reasoning + Prioritization]
        D4[Evidence-Based<br/>Recommendations]
        D5[Sentiment Analysis]
    end

    subgraph Presentation["Presentation Layer"]
        E1[Streamlit Executive Dashboard]
        E2[Live Strategic Query]
    end

    A1 & A2 & A3 & A4 --> B1 --> B2 --> B3 --> B4 --> C1
    C1 --> D1
    D1 --> D2 --> D3 --> D4
    C1 --> D5
    D2 & D3 & D4 & D5 --> E1
    C1 --> E2
    D3 -.local LLM.-> E2
```

**Local reasoning engine:** All LLM-based reasoning (Strategic Intelligence Engine, CEO Agent, Evidence-Based Recommendations, Live Query) runs on **Phi-4 Mini via Ollama**, hosted locally. This satisfies the project requirement that the reasoning engine must be an open-source or freely accessible model, with no paid commercial LLM API involved.

---

## Data Flow Diagram

```mermaid
flowchart LR
    Web([Public Web<br/>DuckDuckGo, Wikipedia,<br/>Google News, Reddit]) -->|live search queries| Raw[Raw Documents<br/>JSON]
    Raw -->|clean + dedupe + filter| Clean[Clean Documents]
    Clean -->|multilingual embedding model| Vectors[384-dim Vectors]
    Vectors -->|store with metadata| Chroma[(ChromaDB)]

    Chroma -->|semantic search| Retrieved[Retrieved Documents]
    Retrieved -->|LLM reasoning| Insights[Risks / Opportunities /<br/>Trends]
    Insights -->|LLM reasoning| CEO[CEO Recommendation<br/>+ Trade-offs]
    CEO -->|LLM reformatting| Evidence[Evidence-Based<br/>Recommendations]

    Chroma -->|sentiment model| Sentiment[News / Public Sentiment<br/>+ Trends]

    Insights & CEO & Evidence & Sentiment --> Dashboard[Streamlit Dashboard]
    Chroma -->|live query| LiveQ[Live Strategic Query]
    LiveQ --> Dashboard
```

---

## Technology Stack

| Layer | Component | Choice | Reason |
|---|---|---|---|
| Collection | Web search | DuckDuckGo (`ddgs`) | Free, no API key, doesn't block automated requests (unlike Google or direct site scraping) |
| Collection | Encyclopedic data | `wikipediaapi` (English + German) | Structured background on Lufthansa Group and its subsidiaries |
| Collection | News | Google News RSS (targeted queries) | Free, live, Lufthansa-specific results |
| Collection | Community | Reddit RSS (`r/lufthansa`) | Genuine community discussion, verified relevant |
| Storage | Knowledge repository | ChromaDB | Stores text, embeddings, and metadata together; built-in persistence and similarity search |
| Storage | Embedding model | `paraphrase-multilingual-MiniLM-L12-v2` | Multilingual (English + German), lightweight, 384-dimension vectors |
| Storage | Similarity metric | Cosine similarity | Measures meaning (vector direction), unaffected by document length |
| Intelligence | Reasoning LLM | Phi-4 Mini via Ollama (local) | Open-source, satisfies "no paid commercial API" requirement, runs locally |
| Intelligence | Sentiment model | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Multilingual, 3-class (positive/negative/neutral), empirically tested as most accurate on business/news text |
| Presentation | Dashboard | Streamlit | Fast to build, interactive widgets, suitable for live demo |
| Presentation | Visualization | Matplotlib + Plotly | Static charts for simple comparisons, interactive charts for trend exploration |

---

## AI Pipeline

The system follows a **Retrieval-Augmented Generation (RAG)** pattern for all reasoning tasks:

```
Retrieval  →  Semantic search in ChromaDB finds the most relevant documents
              for a given question, using cosine similarity over multilingual embeddings

Generation →  The retrieved documents are passed to the local LLM (Phi-4 Mini),
              which reasons over them and generates new, evidence-grounded text —
              risks, opportunities, trends, recommendations, or a live answer
```

This pattern is applied four times across the project:

1. **Strategic Intelligence Engine** — retrieves documents per sub-topic (e.g. competitive threats, regulatory changes) and generates structured risks/opportunities/trends with severity/impact and confidence scores
2. **AI CEO Agent** — takes the intelligence output and generates prioritized strategic recommendations, explicitly reasoning about trade-offs between competing priorities
3. **Evidence-Based Recommendations** — reformats the CEO's priorities into the exact structured format (Recommendation / Supporting Evidence / Expected Impact / Risk Assessment)
4. **Live Strategic Query** — answers any new question, live, using the same retrieval-then-generation pattern, demonstrating the working prototype on demand

**Sentiment Analysis** is deliberately *not* part of the RAG pipeline — it retrieves documents but only classifies them (positive/negative/neutral); no new text is generated, so it does not qualify as RAG.

---

## Design Decisions

**Why DuckDuckGo over Google or direct site scraping**
Google actively blocks automated search requests, and a direct attempt to scrape Lufthansa's own website returned a 403 Forbidden error. DuckDuckGo's `ddgs` library is purpose-built for automated search and does not block this kind of access.

**Why both English and German sources**
Lufthansa is a German company. A meaningful share of its richest content — financial reports, competitive analysis, regulatory and union matters — is published in German first or only in German. Using German search queries and German Wikipedia surfaces content that an English-only collection would miss entirely.

**Why a multilingual embedding model instead of the brief's recommended English-only models**
The brief recommends `BAAI bge-base-en-v1.5`, `BAAI bge-small-en-v1.5`, and `all-MiniLM-L6-v2` — all explicitly English-only models (note the `-en-` in two of the names). Since the collected data is a genuine mix of English and German, an English-only model would fail to properly represent the meaning of German documents during semantic search. `paraphrase-multilingual-MiniLM-L12-v2` was chosen as the natural multilingual variant of the same MiniLM family the brief recommends, preserving the spirit of the recommendation while correctly handling the actual data.

**Why cosine similarity over Euclidean distance**
Collected documents vary enormously in length — from short titles to full Wikipedia extracts. Euclidean distance is sensitive to vector magnitude, which is influenced by document length, and would incorrectly treat longer documents as "further away" even when they share the same meaning. Cosine similarity measures only the angle between vectors, ignoring length, making it the correct choice for a corpus with highly variable document lengths.

**Why a local LLM (Ollama) instead of a cloud API**
The brief explicitly disallows OpenAI, Anthropic, Gemini, and any paid commercial LLM API as the reasoning engine. Phi-4 Mini, run locally via Ollama, is fully open-source and satisfies this requirement without ambiguity, while remaining light enough to run reliably on consumer hardware.

**Why filtering for relevance happens after collection, not instead of broad collection**
RSS feeds from general aviation sources return many articles unrelated to Lufthansa specifically (e.g., about other airlines). Rather than relying on narrow collection alone, documents are collected broadly and then explicitly filtered by checking for mentions of Lufthansa or its subsidiaries — ensuring the final knowledge base is genuinely focused on the company being analyzed.

**Why the CEO Agent must address trade-offs explicitly**
A flat, unranked list of opportunities is information retrieval, not strategy. The CEO Agent's prompt explicitly requires it to state what is being *deprioritized* and *why* the top choice is more urgent than the alternatives — reflecting the reality that Lufthansa, like any organization, has limited resources and cannot pursue every opportunity at once.

**Why the dashboard reads pre-computed results rather than calling the LLM live for every section**
LLM inference on local hardware can be slow and is sensitive to available memory. Pre-computing the Strategic Intelligence Engine, CEO Agent, and Evidence-Based Recommendations ahead of time, then having the dashboard simply read and display the saved results, ensures the dashboard loads quickly and reliably. The separate **Live Strategic Query** feature demonstrates the same underlying retrieval-and-reasoning pipeline working in real time, on demand, without compromising the reliability of the core dashboard sections.

---

## Project Structure

```
lufthansa_intelligence/
├── notebooks/
│   ├── data_collection.ipynb        # Task 1: Live data collection
│   ├── processing.ipynb             # Task 2 + 3: Knowledge repository + processing
│   ├── intelligence_engine.ipynb    # Task 4: Strategic Intelligence Engine
│   ├── ceo_agent.ipynb              # Task 5: AI CEO Agent
│   ├── recommendations.ipynb        # Task 6: Evidence-Based Recommendations
│   └── sentiment_analysis.ipynb     # Dashboard Section 5: Sentiment Analysis
├── data/                            # Saved outputs (documents, intelligence, sentiment, recommendations)
├── storage/
│   └── chromadb/                    # Persistent vector database
├── assets/                          # Dashboard images
├── app.py                           # Streamlit Executive Intelligence Dashboard
├── requirements.txt
├── .env                             # API keys (not committed to GitHub)
└── README.md
```

---

## How to Run

1. Clone the repository and create a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Install and start [Ollama](https://ollama.com), then pull the model: `ollama pull phi4-mini`
4. Add a HuggingFace token to a `.env` file: `HF_TOKEN=your_token_here`
5. Run the notebooks in order (01 → 06) to collect data, build the knowledge repository, and generate intelligence outputs
6. Launch the dashboard: `streamlit run app.py`

