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

## Infrastructure Provisioning

Choose **Option A** (Azure CLI, good for learning each service) or **Option B** (Terraform, repeatable one-command deploy).

### Option A — Azure CLI

> Requires [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) and the Video Indexer extension.

```bash
# ── Install the Video Indexer CLI extension (once) ────────────────────────────
az extension add --name video-indexer --upgrade

# ── Variables — edit these before running ─────────────────────────────────────
RG="healthguard-rg"
LOCATION="eastus"          # GPT-4o regions: eastus | swedencentral | westus
PREFIX="healthguard"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# ── 1. Resource Group ─────────────────────────────────────────────────────────
az group create \
  --name $RG \
  --location $LOCATION

# ── 2. Azure OpenAI ───────────────────────────────────────────────────────────
az cognitiveservices account create \
  --name "${PREFIX}-openai" \
  --resource-group $RG \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0

# GPT-4o deployment
az cognitiveservices account deployment create \
  --name "${PREFIX}-openai" \
  --resource-group $RG \
  --deployment-name "gpt-4o" \
  --model-name "gpt-4o" \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "GlobalStandard"

# text-embedding-3-small deployment
az cognitiveservices account deployment create \
  --name "${PREFIX}-openai" \
  --resource-group $RG \
  --deployment-name "text-embedding-3-small" \
  --model-name "text-embedding-3-small" \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 5 \
  --sku-name "Standard"

# ── 3. Azure AI Search (Standard tier required for vector search) ─────────────
az search service create \
  --name "${PREFIX}-search" \
  --resource-group $RG \
  --location $LOCATION \
  --sku standard

# ── 4. Storage Account (required by Video Indexer) ────────────────────────────
az storage account create \
  --name "${PREFIX}vistorage" \
  --resource-group $RG \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# ── 5. Azure Video Indexer ────────────────────────────────────────────────────
STORAGE_ID=$(az storage account show \
  --name "${PREFIX}vistorage" \
  --resource-group $RG \
  --query id -o tsv)

az videoindexer account create \
  --name "${PREFIX}-vi" \
  --resource-group $RG \
  --location $LOCATION \
  --storage-services "{\"storageAccountId\": \"$STORAGE_ID\"}"

# ── 6. Azure Monitor (Log Analytics + Application Insights) ──────────────────
az monitor log-analytics workspace create \
  --workspace-name "${PREFIX}-law" \
  --resource-group $RG \
  --location $LOCATION

WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --workspace-name "${PREFIX}-law" \
  --resource-group $RG \
  --query id -o tsv)

az monitor app-insights component create \
  --app "${PREFIX}-appinsights" \
  --resource-group $RG \
  --location $LOCATION \
  --workspace "$WORKSPACE_ID"

# ── 7. Service Principal + RBAC ───────────────────────────────────────────────
az ad sp create-for-rbac \
  --name "${PREFIX}-sp" \
  --role Contributor \
  --scopes "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RG}" \
  --json-auth
# Save the JSON output — it contains your AZURE_TENANT_ID, AZURE_CLIENT_ID,
# AZURE_CLIENT_SECRET, and AZURE_SUBSCRIPTION_ID.

# ── 8. Extract all values for .env ────────────────────────────────────────────
echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
echo "AZURE_RESOURCE_GROUP=$RG"
echo "AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name "${PREFIX}-openai" --resource-group $RG \
  --query properties.endpoint -o tsv)"
echo "AZURE_OPENAI_API_KEY=$(az cognitiveservices account keys list \
  --name "${PREFIX}-openai" --resource-group $RG \
  --query key1 -o tsv)"
echo "AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o"
echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small"
echo "AZURE_OPENAI_API_VERSION=2024-10-01-preview"
echo "AZURE_SEARCH_ENDPOINT=https://${PREFIX}-search.search.windows.net"
echo "AZURE_SEARCH_API_KEY=$(az search admin-key show \
  --service-name "${PREFIX}-search" --resource-group $RG \
  --query primaryKey -o tsv)"
echo "AZURE_SEARCH_INDEX_NAME=health-guidelines"
echo "AZURE_VI_NAME=${PREFIX}-vi"
echo "AZURE_VI_LOCATION=$LOCATION"
echo "AZURE_VI_ACCOUNT_ID=$(az videoindexer account show \
  --name "${PREFIX}-vi" --resource-group $RG \
  --query properties.accountId -o tsv)"
echo "AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name "${PREFIX}vistorage" --resource-group $RG \
  --query connectionString -o tsv)"
echo "APPLICATIONINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
  --app "${PREFIX}-appinsights" --resource-group $RG \
  --query connectionString -o tsv)"
```

### Option B — Terraform

> Requires [Terraform >= 1.9](https://developer.hashicorp.com/terraform/install). Provisions all resources in one command (~5-10 min).

```bash
# 1. Copy the vars template and set your subscription_id
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars — fill in subscription_id (required)

# 2. Download providers
terraform -chdir=terraform init

# 3. Preview what will be created (no changes yet)
terraform -chdir=terraform plan

# 4. Provision all Azure resources
terraform -chdir=terraform apply

# 5. Write outputs directly to .env
terraform -chdir=terraform output -raw dot_env > .env
```

> **Tip:** All sensitive outputs (API keys, secrets) are redacted in terminal display.  
> Run `terraform -chdir=terraform output -json` to inspect individual values.

> **Teardown:** `terraform -chdir=terraform destroy` removes every resource created above.

## Project Structure

```
ComplianceQAPipeline/
├── main.py                          # CLI entry point
├── terraform/                       # Infrastructure as Code (Terraform)
│   ├── main.tf                      # Providers + Resource Group
│   ├── openai.tf                    # Azure OpenAI + model deployments
│   ├── search.tf                    # Azure AI Search
│   ├── video_indexer.tf             # Video Indexer + Storage Account
│   ├── monitoring.tf                # App Insights + Log Analytics
│   ├── identity.tf                  # Service Principal + RBAC
│   ├── variables.tf                 # Input variables
│   ├── outputs.tf                   # Outputs → .env values
│   └── terraform.tfvars.example     # Template (copy → terraform.tfvars)
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
└── azure_services_tutorial.ipynb   # Interactive tutorial notebook
```

## Quick Start

### 1. Install dependencies
```bash
uv sync
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your Azure credentials,  
or use **Terraform** / **Azure CLI** from the [Infrastructure Provisioning](#infrastructure-provisioning) section above to generate values automatically:
```bash
cp .env.example .env
# Edit .env with your values, or run: terraform -chdir=terraform output -raw dot_env > .env
```

### 3. Index health guidelines
```bash
uv run python backend/scripts/index_documents.py
```

### 4. Run the API
```bash
uv run uvicorn backend.src.api.server:app --reload
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
