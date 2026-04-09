# HealthGuard AI — TikTok/YouTube Health Claims Auditor

An AI-powered pipeline that audits TikTok and YouTube health videos for misleading claims, unsubstantiated medical advice, and FTC/FDA/WHO guideline violations.

## Architecture

```
TikTok/YouTube URL
       │
       ▼
┌──────────────┐     ┌──────────────────┐
│ index_video  │────▶│ audit_content    │────▶ Health Audit Report
│   (Node 1)   │     │   (Node 2)       │
└──────────────┘     └──────────────────┘
       │                      │
  Azure Video           Azure OpenAI (GPT-4o)
  Indexer               Azure AI Search (RAG)
  + yt-dlp              + Health Guidelines KB
```

**LangGraph** orchestrates a 2-node workflow:
1. **index_video_node** — Downloads video via yt-dlp (YouTube or TikTok), uploads to Azure Video Indexer, extracts transcript + OCR text
2. **audit_content_node** — Retrieves relevant health guidelines via RAG (Azure AI Search), then uses GPT-4o to analyze content for violations

## Azure Services Used

| Service | Purpose |
|---------|---------|
| **Azure Video Indexer** | Extract transcript + OCR from videos |
| **Azure OpenAI** | GPT-4o for analysis, text-embedding-3-small for RAG |
| **Azure AI Search** | Vector store for health guidelines (RAG) |
| **Azure Identity** | Service principal authentication |
| **Azure Monitor** | OpenTelemetry-based observability |

## Project Structure

```
ComplianceQAPipeline/
├── main.py                          # CLI entry point
├── backend/
│   ├── data/                        # Health guidelines knowledge base
│   │   ├── ftc-health-claims-guidance.md
│   │   └── who-fda-health-misinformation-guidelines.md
│   ├── scripts/
│   │   └── index_documents.py       # Index docs → Azure AI Search
│   └── src/
│       ├── api/
│       │   ├── server.py            # FastAPI REST API
│       │   └── telemetry.py         # Azure Monitor setup
│       ├── graph/
│       │   ├── nodes.py             # LangGraph node logic
│       │   ├── state.py             # TypedDict state schema
│       │   └── workflow.py          # Graph compilation
│       └── services/
│           └── video_indexer.py     # Azure Video Indexer + yt-dlp
├── azure_functions/
│   └── function_app.py             # Azure Functions trigger
└── azure_services_tutorial.ipynb   # Interactive tutorial notebook
```

## Quick Start

### 1. Install dependencies
```bash
pip install -e .
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your Azure credentials:
```bash
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_SUBSCRIPTION_ID=...
AZURE_RESOURCE_GROUP=...
AZURE_VI_ACCOUNT_ID=...
AZURE_VI_LOCATION=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_API_KEY=...
AZURE_SEARCH_INDEX_NAME=...
```

### 3. Index health guidelines
```bash
cd ComplianceQAPipeline
python backend/scripts/index_documents.py
```

### 4. Run the API
```bash
uvicorn backend.src.api.server:app --reload
```

### 5. Audit a video (by URL)
```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.tiktok.com/@drjasonf/video/7349282018498686254"}'
```

### 6. Audit a video (by file upload)
```bash
curl -X POST http://localhost:8000/audit/upload \
  -F "file=@test_video.mp4"
```
Or use the interactive Swagger UI at **http://localhost:8000/docs** to upload via browser.

## Violation Categories

The auditor checks for:
- **Unsubstantiated Health Claim** — Claims without scientific evidence
- **Misleading Medical Advice** — Content that could cause harm
- **Dangerous Recommendation** — Advice to stop medication or avoid doctors
- **Undisclosed Sponsorship** — Paid promotions without disclosure
- **Fake Authority** — Claiming credentials not held
- **Deceptive Testimonial** — Fabricated or misleading success stories

## Tech Stack

- **Python 3.12** with uv package manager
- **LangGraph** — Stateful workflow orchestration
- **LangChain** — Azure OpenAI + AI Search integration
- **FastAPI** — REST API server
- **yt-dlp** — Multi-platform video downloader
- **OpenTelemetry** — Distributed tracing
