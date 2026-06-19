# 🌌 Nexus_AI
### *The Agentic Unstructured-to-Action Intelligence Engine*

![Architecture Diagram](./architecture.png)

---

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![pgvector](https://img.shields.io/badge/Vector-pgvector-green.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🎯 Project Vision & Purpose

### The Problem: The "Dark Data" Crisis
In the modern enterprise, the most valuable knowledge is trapped in **"Dark Data"**—unstructured, fragmented files like messy PDFs, legacy spreadsheets, recorded meeting MP4s, and scattered PowerPoint decks. This data is invisible to traditional search engines and unusable for standard LLMs because it lacks structure and scale.

### The Solution: Nexus_AI
Nexus_AI is not just a chatbot; it is a **complete intelligence refinery**. The goal is to build a system that can "sense" any file format, "remember" its semantic meaning with mathematical precision, and eventually "act" on that information autonomously. 

👉 **Nexus_AI bridges between raw binary files and actionable AI intelligence.**

---

### 🛠️ The Journey So Far
Nexus_AI is engineered in modular stages to ensure production-grade stability:

- **Part 1 (The Senses):**  
  A high-performance multimodal ingestion engine that extracts signals from noise across 14+ data formats.

- **Part 2 (The Memory):**  
  A hybrid vector memory bank using `pgvector` for sub-millisecond semantic retrieval.

- **Part 3 (The Brain & API):**  
  A robust FastAPI backend that routes queries to powerful LLMs (like Groq) and performs Retrieval-Augmented Generation (RAG).

- **Part 4 (The Face & Deployment):**  
  A beautiful, interactive Streamlit Web UI deployed using a **100% Zero-Cost Cloud Architecture** (Supabase, Render, Streamlit Cloud).

---

## 🧬 Deep Dive: Engineering Implementation

### 🧩 Part 1: The Multimodal Ingestion Engine

We built a **"Universal Translator"** for data, supporting **14+ formats** including Documents (PDF, TXT), Tabular (CSV), Vision (JPG), Media (MP3, MP4), and Archives (ZIP).

#### ⚠️ Challenges & Engineering Solutions
| Format | The Technical Challenge | The Engineering Solution |
| :--- | :--- | :--- |
| **PDF** | Tables are often read as jumbled text strings. | **Hybrid Approach**: `PyMuPDF` for text and `Camelot` for tabular linearization. |
| **Media** | Massive ML models crashing local RAM. | **Cloud Offloading**: Replaced local Whisper with **Groq's Cloud Whisper API** (`whisper-large-v3`) via async HTTP streaming. |
| **Archives** | Recursive "Zip-Bombs". | Built a **Recursive Unpacker** using `zipfile` that feeds discovered files back into the dispatcher. |

---

### 🧠 Part 2: The Hybrid Memory Bank

#### 🚀 The Technology Choice: PostgreSQL + pgvector + Supabase
Bypassed purely vector databases (Pinecone, Chroma) for:
1. **ACID Compliance:** Strict consistency.
2. **Hybrid Querying:** Metadata filtering + vector search in **one single SQL query**.
3. **Zero Vendor Lock-in:** Open-source extension, currently hosted entirely for free on **Supabase**.

---

### 🌐 Part 3: Zero-Cost Cloud Deployment Architecture

To make this project portfolio-ready and live 24/7 without spending a dime, we engineered a **Zero-Cost Cloud Architecture**:

1. **LLM Inference (Groq):** Used Groq's free tier for blazing-fast Llama-3 inference and Whisper audio transcription, integrated via Base URL overrides in the OpenAI SDK.
2. **Database (Supabase):** Hosted our PostgreSQL + `pgvector` database on Supabase's generous free tier.
3. **Backend API (Render):** Deployed the FastAPI server to Render, with CORS middleware enabled to allow secure cross-origin requests.
4. **Frontend UI (Streamlit Cloud):** Built a stateful chat interface (`st.session_state`) and deployed it directly from GitHub using Streamlit Community Cloud.

---

## 🛠️ Tech Stack Checklist

### ✅ Completed Modules

- [x] **Part 1: Multimodal Ingestion Engine** (`PyMuPDF`, `Groq Whisper`, `python-magic`)  
- [x] **Part 2: Hybrid Memory Bank** (`PostgreSQL`, `pgvector`, `Supabase`)  
- [x] **Part 3: Secure API Gateway** (`FastAPI`, `CORS Middleware`, `Uvicorn`)  
- [x] **Part 4: Generative Brain** (`OpenAI SDK`, `Groq Llama-3.1`)  
- [x] **Part 5: Frontend UI** (`Streamlit`, `st.session_state`, `Requests`)  
- [x] **Part 6: Cloud Deployment** (`Render`, `Streamlit Cloud`, `GitHub Integration`)  

### ⏳ Future Modules

- [ ] **Part 7: Agentic Orchestration** (LangGraph workflows, Tool Calling)  
- [ ] **Part 8: Advanced RAG** (Cross-Encoder Reranking)  

---

## 🚀 Quick Start (Local Development)

### 1. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
LLM_PROVIDER="groq"
GROQ_API_KEY="gsk_your_key_here"
DATABASE_URL="postgresql://postgres.[YOUR-PROJECT]:[YOUR-PASSWORD]@aws-0-region.pooler.supabase.com:6543/postgres"
```

### 2. Install Dependencies
```bash
# We use 'uv' for lightning-fast Python package management
uv sync
```

### 3. Run the Stack (Two Terminals)

**Terminal 1 (Backend):**
```bash
uv run uvicorn src.api.server:app --reload
```

**Terminal 2 (Frontend):**
```bash
uv run streamlit run frontend/app.py
```

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
