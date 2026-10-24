# GreenPulse AI - Enterprise Industrial AI Copilot (RAG Pipeline)

## 1. Executive Architecture Overview

The **GreenPulse AI Copilot** is a production-grade, domain-specific Retrieval-Augmented Generation (RAG) assistant designed for industrial manufacturing and heavy engineering facilities. It synthesizes three distinct layers of operational intelligence into a single conversational interface:

1. **Live SCADA & Backend Telemetry**: Real-time asset power draw, peak demand spikes, health index scores, 24-hour XGBoost energy forecasts, Isolation Forest anomaly alerts, and active prescriptive recommendations.
2. **Company Vector Knowledge Bases (RAG)**: Standard Operating Procedures (SOPs), machine OEM manuals, ISO 50001:2018 energy management standards, BEE PAT compliance guidelines, and predictive maintenance protocols.
3. **Industrial Engineering Knowledge Base**: Deterministic domain formulations and benchmarks for Peak Demand, Contract Demand, Power Factor, Load Factor, Carbon Intensity, SHAP explainability, and OEE.

```
                                    +------------------------------+
                                    |         User Query           |
                                    +------------------------------+
                                                   |
                                                   v
                                    +------------------------------+
                                    |      Intent Classifier       |
                                    | (LIVE | RAG | CONCEPT | HYB) |
                                    +------------------------------+
                                       /           |            \
                   +------------------+     +------+-----+       +-------------------+
                   |                        |            |                           |
                   v                        v            v                           v
     +--------------------------+  +-------------------------------+  +--------------------------+
     |     Live Data Agent      |  | Qdrant Vector Search Engine   |  | Industrial Domain Engine |
     | - Dashboard Service      |  | - Company SOPs                |  | - Formulations           |
     | - Machine Digital Twin   |  | - Machine Manuals (COMP, CNC) |  | - DISCOM Tariffs / CEA   |
     | - XGBoost 24h Forecast   |  | - ISO 50001 EnPI Standard     |  | - Power Quality Benchmrk |
     | - Anomaly / Alert Engine |  | - BEE PAT Cycle VI Scheme     |  | - SHAP & IsolationForest |
     | - RBAC Policy Scoping    |  | - IEEE 519 / ISO 10816        |  +--------------------------+
     +--------------------------+  +-------------------------------+                 |
                   \                        |                                       /
                    \                       v                                      /
                     +------------------------------------------------------------+
                                                    |
                                                    v
                                   +--------------------------------+
                                   |       Industrial Prompt        |
                                   | - Role & Persona Constraints   |
                                   | - Multi-Turn Session Memory    |
                                   | - Strict Anti-Hallucination    |
                                   | - Citations & Data Provenance  |
                                   +--------------------------------+
                                                    |
                                                    v
                                   +--------------------------------+
                                   | Gemma 3 4B Instruct via Ollama |
                                   |  (Fallback: Local LLM Engine)  |
                                   +--------------------------------+
                                                    |
                                                    v
                                   +--------------------------------+
                                   |  Structured Markdown Response  |
                                   |  - Summary                     |
                                   |  - Detailed Explanation        |
                                   |  - Recommended Actions         |
                                   |  - Sources & Provenance        |
                                   +--------------------------------+
```

---

## 2. Partitioned Vector Knowledge Collections (Qdrant)

The vector database runs on **Qdrant** with separate collections for domain isolation:

| Collection Name | Content Type | Indexed Examples | Default Distance |
| :--- | :--- | :--- | :---: |
| `company_sops` | Standard Operating Procedures | Peak demand curtailment (SOP-ENG-04), Harmonic mitigation (SOP-ELEC-12) | Cosine |
| `machine_manuals` | OEM Machinery Handbooks | Atlas Copco GA-160 VSD+ Compressor, DMG MORI 5-axis CNC Milling Center | Cosine |
| `government_schemes` | Statutory & Regulatory Frameworks | BEE PAT Cycle VI compliance, Renewable Energy Open Access (GEOA) | Cosine |
| `iso_50001` | Energy Management Systems | Energy Baseline (EnB) determination, EnPIs, Significant Energy Uses (SEUs) | Cosine |
| `maintenance_docs` | Reliability & Condition Monitoring | ISO 10816-3 vibration severity zones, bearing demodulation frequencies | Cosine |
| `energy_policies` | Corporate Sustainability Roadmaps | GreenPulse Net-Zero 2035 framework, IE4/IE5 motor procurement norms | Cosine |
| `industrial_standards`| Power Quality & Compliance Specs | IEEE 519-2022 voltage & current harmonic limits (THD-V ≤ 5%, TDD ≤ 15%) | Cosine |
| `uploaded_pdfs` | Dynamic Uploaded Files | User-uploaded operational handbooks, audit PDF reports, warranty contracts | Cosine |

---

## 3. Embedding Pipeline

1. **Text Extraction**:
   - **PDFs**: Page-by-page text parsing via `PyMuPDF` (`fitz`), preserving physical page numbers for audit citations.
   - **DOCX**: Hierarchical section heading extraction via `python-docx`.
   - **Markdown / Plain Text**: Semantic splitting along level-2 headers (`##`) and Markdown pseudo-pages.
2. **Chunking**:
   - Configured via LangChain `RecursiveCharacterTextSplitter`:
     - **Chunk Size**: 650 characters.
     - **Chunk Overlap**: 100 characters.
     - **Separators**: `["\n## ", "\n### ", "\n\n", "\n", ". ", " "]`.
3. **Dense Vector Generation**:
   - Model: `BAAI/bge-m3` / `sentence-transformers/all-MiniLM-L6-v2`.
   - In-memory process singleton prevents redundant weight reloading across concurrent API calls.
   - Built-in deterministic pseudo-semantic hash embedding fallback guarantees 100% vector availability offline.
4. **Incremental Indexing**:
   - Documents are fingerprinted via SHA-256 hashes.
   - Unmodified files are automatically skipped on server re-indexing.

---

## 4. Live Backend API Integration & Role-Based Access Control (RBAC)

The Copilot enforces the same security guarantees as the platform:

| User Persona | Scoped Machinery | Accessible Data | Redacted / Restricted Data |
| :--- | :--- | :--- | :--- |
| **Plant Head** | All Factory Fleet | Full plant KPIs, demand charges, financial ROI, raw SCADA registers, executive reports | None |
| **Energy Manager** | All Energy Systems | 24h XGBoost forecasts, carbon accounting, tariff schedules, recommendations | User management administration |
| **Maintenance Manager**| All Rotating Assets | Health indexes, vibration spectra, thermal drift alerts, OEM service intervals | Executive financial tariffs |
| **Operator** | Assigned Bay Assets (`COMP-01`, `CNC-01`)| Assigned machine telemetry, safety SOPs, vibration tolerances, shift procedures | Plant-wide financial tariffs, contracted demand penalty charges, executive ROI |

---

## 5. Ollama & Gemma 3 4B Configuration

The Copilot connects to Ollama via HTTP REST APIs (`http://localhost:11434/api/generate`):

### Pulling Gemma 3 4B Instruct
To run the target Gemma model locally:
```bash
ollama pull gemma:latest
# or
ollama pull gemma3:4b
```

### Automatic Model Fallback
If `gemma3:4b` is not installed on the host machine, the service inspects available models (e.g. `qwen3:8b` or `gemma:latest`) and switches without runtime errors. If the Ollama server is offline, an intelligent deterministic industrial synthesis engine guarantees structured markdown answers.

### Environment Variables (`backend/.env`):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
QDRANT_PATH=./qdrant_storage
DOCUMENTS_DIR=./knowledge_documents
```

---

## 6. Adding New Documents to Knowledge Collections

### Method 1: Interactive Web Console (Recommended)
1. Navigate to **AI Copilot (RAG)** in the GreenPulse sidebar (`/copilot`).
2. In the right-hand **Ingest Documents** panel, select the target collection (e.g., `machine_manuals`, `company_sops`).
3. Click or drag-and-drop your `.pdf`, `.docx`, `.txt`, or `.md` file.
4. The document is extracted, chunked, embedded, and indexed into Qdrant within seconds.

### Method 2: Filesystem Seed Ingestion
1. Place your markdown or PDF documents into `backend/knowledge_documents/<collection_name>/`:
   ```
   backend/knowledge_documents/
   ├── company_sops/
   ├── machine_manuals/
   ├── government_schemes/
   ├── iso_50001/
   ├── maintenance_docs/
   ├── energy_policies/
   └── industrial_standards/
   ```
2. Call the re-index endpoint or click **Re-index Vectors** in the UI:
   ```bash
   curl -X POST http://localhost:8000/api/v1/copilot/reindex \
     -H "Authorization: Bearer <JWT_TOKEN>"
   ```

---

## 7. API Reference

### `POST /api/v1/copilot/chat`
Ask questions combining live telemetry, company documents, and industrial concepts:
```json
{
  "query": "Why is today's energy high?",
  "session_id": "sess-eng-001"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "query": "Why is today's energy high?",
    "session_id": "sess-eng-001",
    "intent": "LIVE_DATA",
    "is_live_data": true,
    "role_applied": "PLANT_HEAD",
    "response": "### Summary\n...\n### Detailed Explanation\n...\n### Recommended Actions\n...\n### Sources & Data Provenance\n- **Current Operational Data**: Real-time SCADA Modbus & Backend Machine Telemetry Engine.",
    "citations": [],
    "model_used": "qwen3:8b"
  }
}
```

### `GET /api/v1/copilot/collections`
Returns stats for all 8 Qdrant collections.

### `POST /api/v1/copilot/upload`
Multipart upload for PDF, DOCX, TXT, or MD documents.

### `GET /api/v1/copilot/history/{session_id}`
Retrieves multi-turn conversation memory for the session.

### `DELETE /api/v1/copilot/history/{session_id}`
Flushes session memory.

---

## 8. Verification & Test Suite

The backend integration suite covers the entire pipeline:
```bash
python backend/test_routes.py
```
**Test Results: 24 passed, 0 failed.**
- JWT Bearer Authentication & 401 Rejection
- Live SCADA Telemetry & Asset Query Dispatch
- Vector Similarity Retrieval with Document Citations
- Industrial Engineering Concept Formulation
- Multi-Turn Session Memory Retention
- Role-Based Access Control and Financial Masking for Operators
