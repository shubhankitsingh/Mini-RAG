# 🔍 Track 2 (Mini-RAG)

A production-ready **Retrieval-Augmented Generation (RAG)** application with inline citations. Built with Python FastAPI backend and React frontend.


---

## 🏗️ Architecture Overview

<img width="902" height="932" alt="brave_screenshot_webwhiteboard com" src="https://github.com/user-attachments/assets/5287edae-e4f0-46b3-a03a-3afe623b5b9b" />



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
git clone https://github.com/shubhankitsingh/Mini-RAG.git
cd Mini-RAG
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

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/ingest` | Ingest text content | `{ text, title, source }` |
| `POST` | `/ingest/file` | Upload and ingest file | `multipart/form-data` |
| `POST` | `/query` | Query with RAG pipeline | `{ query, top_k, rerank_top_k }` |
| `DELETE` | `/clear` | Clear all vectors | - |
| `GET` | `/stats` | Get database statistics | - |
| `GET` | `/health` | Health check | - |

### Example API Usage

**Ingest Text:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document content here", "title": "My Document", "source": "manual"}'
```

**Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the return policy?", "top_k": 10, "rerank_top_k": 5}'
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description | Where to Get |
|----------|----------|-------------|--------------|
| `GOOGLE_API_KEY` | ✅ | Gemini API for embeddings | [Google AI Studio](https://aistudio.google.com/) |
| `PINECONE_API_KEY` | ✅ | Vector database access | [Pinecone Console](https://app.pinecone.io/) |
| `COHERE_API_KEY` | ✅ | Reranker API | [Cohere Dashboard](https://dashboard.cohere.com/) |
| `GROQ_API_KEY` | ✅ | LLM inference | [Groq Console](https://console.groq.com/) |

### Frontend (Vercel Environment)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ (production) | Backend API URL (e.g., `https://your-api.onrender.com`) |

---

## 🧪 Evaluation

Run the gold set evaluation to test RAG quality:

```bash
cd backend/tests
python test_eval.py
```

### Evaluation Results

| Metric | Score | Description |
|--------|-------|-------------|
| **Success Rate** | 100% (5/5) | All queries returned expected answers |
| **Precision** | 100% | All retrieved chunks were relevant |
| **Recall** | 100% | All relevant documents were retrieved |
| **Citation Accuracy** | 100% | Citations correctly map to source documents |
| **Avg Keywords Match** | 77% | Percentage of expected keywords in response |
| **Avg Citations/Query** | 5.0 | Number of source citations per answer |

### Gold Set Test Cases

| # | Query | Expected Source | Result |
|---|-------|-----------------|--------|
| 1 | What is the return policy? | Returns & Refunds Policy | ✅ PASS |
| 2 | What are the security best practices? | Security Guidelines | ✅ PASS |
| 3 | How long does shipping take? | Shipping FAQ | ✅ PASS |
| 4 | What is the battery capacity? | X100 Power Station Specs | ✅ PASS |
| 5 | What is the employee vacation policy? | NONE (unrelated) | ✅ PASS |

### Sample Output
```
🧪 RAG EVALUATION - GOLD SET TEST
==================================

Q1: What is the return policy?
   Expected Source: Returns & Refunds Policy
   ✅ PASS - Keywords: 100%, Citations: 5

Q5: What is the employee vacation policy?
   Expected Source: NONE - Unrelated
   ✅ PASS - Correctly identified as unrelated (no info)

══════════════════════════════════════════════════════════════
📊 EVALUATION SUMMARY
══════════════════════════════════════════════════════════════
Success Rate: 5/5 (100.0%)
Avg Keyword Score: 77.0%
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

## � Deployment

### Backend - Render (Free Tier)

1. **Connect GitHub Repo** to [Render](https://render.com)
2. **Create Web Service:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Add Environment Variables:**
   ```
   GOOGLE_API_KEY=your_key
   PINECONE_API_KEY=your_key
   COHERE_API_KEY=your_key
   GROQ_API_KEY=your_key
   ```
4. **Deploy** - Takes ~2-3 minutes

### Frontend - Vercel (Free Tier)

1. **Import GitHub Repo** to [Vercel](https://vercel.com)
2. **Configure:**
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
3. **Add Environment Variable:**
   ```
   VITE_API_URL=https://your-render-backend.onrender.com
   ```
4. **Deploy** - Takes ~1 minute

### Deployment Architecture

```
┌─────────────────┐         ┌─────────────────┐
│     Vercel      │         │     Render      │
│   (Frontend)    │────────▶│    (Backend)    │
│   React + Vite  │  HTTPS  │    FastAPI      │
└─────────────────┘         └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             ┌──────────┐     ┌──────────┐     ┌──────────┐
             │ Pinecone │     │  Cohere  │     │   Groq   │
             │ (Vectors)│     │(Reranker)│     │  (LLM)   │
             └──────────┘     └──────────┘     └──────────┘
```

### Live Demo

- **Frontend:** [your-app.vercel.app](https://your-app.vercel.app)
- **Backend API:** [your-api.onrender.com](https://your-api.onrender.com)
- **API Docs:** [your-api.onrender.com/docs](https://your-api.onrender.com/docs)

---

## �📝 Remarks (Limits, Trade-offs & Future Work)

### Limits Encountered During Development

| Issue | Cause | Solution |
|-------|-------|----------|
| **Pinecone package rename** | `pinecone-client` → `pinecone` | Updated requirements.txt |
| **Python 3.13 compatibility** | Strict version pins failed | Changed to flexible versions (`>=`) |
| **Document overwrites** | Chunk IDs based only on position | Added content hash to ID generation |
| **CORS errors** | Frontend-backend cross-origin | Added `allow_origins=["*"]` middleware |
| **Cohere rate limits** | Free tier: 10 req/min | Added retry logic with backoff |
| **Large file uploads** | Memory issues on free tier | Limited to text files, chunked processing |

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

- 🐙 Resume: [**Shubhankit Singh**](https://drive.google.com/drive/u/1/folders/1fbz70wkgYIyN5PUa1ITZKRwDW8uCJ12L)

---
