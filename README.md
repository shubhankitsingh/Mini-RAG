# 🔍 RAG Knowledge Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** application with inline citations. Built with Python FastAPI backend and React frontend.

> **Author:** [Your Name](https://linkedin.com/in/YOUR_LINKEDIN)  
> **Resume:** [View Resume](https://your-resume-link.com)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                           React + Vite + Tailwind                            │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    │
│  │  Upload/Paste   │    │   Query Input    │    │  Answer + Citations │    │
│  │    Documents    │    │                  │    │                     │    │
│  └────────┬────────┘    └────────┬─────────┘    └──────────▲──────────┘    │
└───────────┼──────────────────────┼─────────────────────────┼────────────────┘
            │                      │                         │
            ▼                      ▼                         │
┌───────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                     │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         INGESTION PIPELINE                            │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐ │   │
│  │  │  Chunking   │──▶│  Embedding  │──▶│  Metadata   │──▶│  Upsert  │ │   │
│  │  │ 1000 tokens │   │   Gemini    │   │  (source,   │   │ Pinecone │ │   │
│  │  │ 10% overlap │   │             │   │   title)    │   │          │ │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                          QUERY PIPELINE                               │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────────┐  │   │
│  │  │  Embed   │──▶│ Retrieve │──▶│ Rerank   │──▶│ Generate Answer │  │   │
│  │  │  Query   │   │  Top-10  │   │  Cohere  │   │   Groq Llama3   │  │   │
│  │  │  Gemini  │   │ Pinecone │   │  Top-5   │   │  + Citations    │  │   │
│  │  └──────────┘   └──────────┘   └──────────┘   └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────┘
            │                      │                         │
            ▼                      ▼                         ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────────┐
│     PINECONE      │  │      COHERE       │  │           GROQ                │
│   Vector Store    │  │     Reranker      │  │      LLM Inference            │
│   768 dimensions  │  │   rerank-v3.5     │  │   llama-3.3-70b-versatile     │
│   Serverless      │  │                   │  │                               │
└───────────────────┘  └───────────────────┘  └───────────────────────────────┘
```

---

## 🚀 Features

- ✅ **Document Ingestion** - Upload text files or paste content directly
- ✅ **Smart Chunking** - 1000 tokens with 10% overlap, sentence-aware splitting
- ✅ **Vector Search** - Pinecone serverless for scalable similarity search
- ✅ **Reranking** - Cohere rerank-v3.5 for improved relevance
- ✅ **LLM Generation** - Groq Llama 3.3 70B for fast, quality responses
- ✅ **Inline Citations** - [1], [2], [3] style citations with expandable sources
- ✅ **FREE APIs** - Uses free tiers of Gemini, Cohere, Groq, and Pinecone

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI endpoints
│   │   ├── rag_engine.py    # Core RAG logic
│   │   └── models.py        # Pydantic schemas
│   ├── tests/
│   │   ├── test_eval.py     # Gold set evaluation
│   │   └── list_chunks.py   # Database inspection
│   ├── requirements.txt
│   └── .env                 # API keys (not in repo)
├── frontend/
│   ├── src/
│   │   └── App.jsx          # React UI
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI (Python) | REST API server |
| **Frontend** | React + Vite + Tailwind | User interface |
| **Embeddings** | Google Gemini `text-embedding-004` | 768-dim vectors (FREE) |
| **Vector DB** | Pinecone Serverless | Cloud vector storage |
| **Reranker** | Cohere `rerank-v3.5` | Result relevance scoring |
| **LLM** | Groq `llama-3.3-70b-versatile` | Answer generation |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys (all have free tiers):
  - [Google AI Studio](https://aistudio.google.com/) - Gemini API
  - [Pinecone](https://www.pinecone.io/) - Vector database
  - [Cohere](https://cohere.com/) - Reranker
  - [Groq](https://groq.com/) - LLM inference

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/mini-rag.git
cd rmini-rag
```

### 2. Setup Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configure API Keys

Create `backend/.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
COHERE_API_KEY=your_cohere_api_key
GROQ_API_KEY=your_groq_api_key
```

### 4. Create Pinecone Index

Go to [Pinecone Console](https://app.pinecone.io/) and create an index:
- **Name:** `mini-rag`
- **Dimensions:** `768`
- **Metric:** `cosine`
- **Type:** Serverless (AWS us-east-1)

### 5. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 6. Setup & Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 7. Access the App

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingest` | Ingest text content |
| `POST` | `/ingest/file` | Upload and ingest file |
| `POST` | `/query` | Query with RAG pipeline |
| `DELETE` | `/clear` | Clear all vectors |
| `GET` | `/stats` | Get database statistics |
| `GET` | `/health` | Health check |

---

## 🧪 Evaluation

Run the gold set evaluation to test RAG quality:

```bash
cd backend/tests
python test_eval.py
```

**Sample Output:**
```
Q1: What is the return policy?
   Expected Source: Returns & Refunds Policy
   ✓ PASS - Keywords: 100%, Citations: 5

Q5: What is the employee vacation policy?
   Expected Source: NONE - Unrelated
   ✓ PASS - Correctly identified as unrelated (no info)

EVALUATION SUMMARY
Success Rate: 5/5 (100%)
Avg Keyword Score: 77%
Avg Citations: 5.0
```

---

## 🔧 Configuration

Key parameters in `backend/app/rag_engine.py`:

```python
CHUNK_SIZE = 1000        # tokens per chunk
CHUNK_OVERLAP = 100      # 10% overlap
EMBEDDING_DIMENSIONS = 768
INDEX_NAME = "mini-rag"
RERANK_MODEL = "rerank-v3.5"
LLM_MODEL = "llama-3.3-70b-versatile"
```

---

## �️ Index Configuration (Track B)

### Pinecone Index Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Index Name** | `mini-rag` | Descriptive, project-specific |
| **Dimensions** | `768` | Matches Gemini `text-embedding-004` output |
| **Metric** | `cosine` | Best for semantic similarity |
| **Cloud** | AWS | Low latency, reliable |
| **Region** | `us-east-1` | Free tier availability |
| **Type** | Serverless | Auto-scaling, cost-effective |

### Vector Metadata Schema

Each vector stored in Pinecone includes:

```json
{
  "id": "md5_hash_of_source_position_content",
  "values": [768-dimensional float array],
  "metadata": {
    "source": "unique_document_identifier",
    "title": "Document Title",
    "section": "",
    "position": 0,
    "chunk_index": 0,
    "total_chunks": 3,
    "text": "The actual chunk text content..."
  }
}
```

### Chunking Strategy

| Parameter | Value | Why |
|-----------|-------|-----|
| **Chunk Size** | 1000 tokens | Balance between context and precision |
| **Overlap** | 100 tokens (10%) | Prevents context loss at boundaries |
| **Splitting** | Sentence-aware | Preserves semantic coherence |

---

## 📝 Remarks (Limits, Trade-offs & Future Work)

### Current Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Text-only ingestion** | No PDF/DOCX support | Convert to text before upload |
| **Single index** | No multi-tenant isolation | Add namespace per user |
| **No persistence** | Frontend state lost on refresh | Add localStorage/session |
| **Free tier rate limits** | May throttle under load | Implement request queuing |

### Design Trade-offs

| Decision | Trade-off | Reasoning |
|----------|-----------|-----------|
| **Gemini embeddings** | Smaller dims (768 vs 1536) | FREE tier, sufficient quality |
| **Groq LLM** | Less customizable than OpenAI | 10x faster inference, FREE |
| **Cohere reranker** | Extra latency (~1s) | Significant relevance improvement |
| **1000 token chunks** | May split related content | Good balance for most docs |
| **Top-10 retrieve, Top-5 rerank** | May miss edge cases | Optimal cost/quality ratio |

### What I'd Do Next

1. **Hybrid Search** - Add BM25 keyword search alongside vector search for better recall
2. **PDF/DOCX Support** - Integrate `pypdf` and `python-docx` for file parsing
3. **Streaming Responses** - Use SSE for real-time LLM output display
4. **Caching Layer** - Redis cache for repeated queries
5. **User Authentication** - JWT-based auth with per-user namespaces
6. **Analytics Dashboard** - Track query patterns, latency, and success rates
7. **Fine-tuned Reranker** - Train domain-specific reranker on user feedback
8. **Evaluation Pipeline** - Automated RAGAS/DeepEval scoring on CI/CD

---

## �📝 Usage

1. **Add Documents**: Paste text or upload `.txt` files
2. **Ask Questions**: Type your query in the search box
3. **View Citations**: Click on citation numbers to expand source text

---

## 🙋 Author

**[Your Name]**

- 📧 Email: your.email@example.com
- 💼 LinkedIn: [linkedin.com/in/YOUR_LINKEDIN](https://linkedin.com/in/YOUR_LINKEDIN)
- 📄 Resume: [View Resume](https://your-resume-link.com)
- 🐙 GitHub: [github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)

---
