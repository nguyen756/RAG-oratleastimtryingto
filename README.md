# Custom Naive RAG Engine (Microservice Architecture)



## Overview
A full-stack, containerized Retrieval-Augmented Generation (RAG) system initially built to parse Wikipedia, customized a bit to extract, embed, and query skill data from Toram Online. 


Instead of using the character-limit chunking method, this uses chunking for a specific regex pattern in the skill data(`get_text_pdf_plib`), but can also be turned off by using a regular `get_text_pdf`. The infrastructure is decoupled into a Node.js frontend and a Python FastAPI backend, orchestrated entirely via Docker Compose for complete environment parity.

*Note: The original Wikipedia BeautifulSoup scraper and standard PDF OCR pipelines are not deprecated. They are preserved in the codebase as modular, uncommentable data-ingestion pipelines for future domain expansion.*

## Pipeline Architecture

1. **Extraction & Semantic Chunking (Data Engineering):**
   - **Primary (PDFs):** Uses `PyMuPDF` to read local PDF texts. Bypasses standard newline-stripping issues by implementing custom Regex (`r"\|\s*#[^\s]+"`) to cleanly slice text precisely at skill tree boundaries (`#blade-skills🗡` and such).
   - **Toggleable (Wikipedia):** Uses `BeautifulSoup4` to target `bodyContent` `<div>` tags, stripping noise (tables, scripts) and applying custom `clean_text()` utilities to normalize unicode and fix HTML escaping.
   - Generates `SHA-1` hashes for data chunks to ensure future deduplication.

2. **Vector Persistence & Embedding:**
   - Powered by `sentence-transformers/all-MiniLM-L6-v2`.
   - Uses `FAISS` with `IndexFlatL2` Euclidean distance retrieval.
   - Implements hard-drive persistence: saves both the mathematical vectors (`.index`) and the text payloads (`metadata.json`) to prevent data amnesia across server reboots.

3. **Backend Microservice (Python):**
   - `FastAPI` serving the ML engine on port `8080`.
   - Pre-loads the FAISS index into RAM at startup to eliminate search latency.
   - Injects the retrieved context into the Gemini API System Prompt.

4. **Frontend UI (Node.js):**
   - An `Express.js` web server rendering a `Handlebars` UI on port `3000`.
   - Communicates securely with the Python backend via Docker's internal `host.docker.internal` / DNS routing.

5. **Orchestration & Security (DevOps):**
   - Managed via `docker-compose.yml`.
   - Utilizes Multi-Stage Docker builds and Alpine Linux base images to minimize attack surfaces and image bloat.
   - Enforces the Principle of Least Privilege by executing containers as the restricted `node` user rather than `root`.
   - Strictly manages secrets (API keys) via `.env` injection at runtime, protected by `.dockerignore`.

## Current Limitations & Engineering Realities
- **Context Confusion:** Currently restricted to `top_k=1`. Injecting multiple skill blocks (`top_k=5`) caused the LLM to hallucinate or cross-contaminate math between different skills. 
- **The Rulebook Bottleneck:** Attempting to hardcode game mechanics into the LLM System Prompt proved highly inefficient and token-expensive.
- **Future Solution:** The next architectural step is replacing the simple Regex extraction with **Metadata Filtering** (tagging FAISS vectors by weapon type) to isolate searches and eliminate cross-contamination without bloating the prompt.

## Tech Stack
* **DevOps / Infra:** `Docker`, `Docker Compose`
* **Backend:** `Python 3.12+`, `FastAPI`, `Uvicorn`
* **Frontend:** `Node.js v24.12`, `Express`, `Handlebars`
* **Data / ML:** `PyMuPDF`, `FAISS-cpu`, `SentenceTransformers`, `Gemini API`, `BeautifulSoup4`

## Quick Start
To spin up the entire microservice environment locally:

1. Clone the repository.
2. Create a `.env` file in the root directory and add your API key: `GEMINI_API_KEY=your_key_here`
3. Build and launch the cluster:
   ```bash
   docker-compose up --build
4. Access the UI at http://localhost:3000.
## Cloud Architecture & CI/CD Pipeline
The backend ML microservice is fully automated and deployed to AWS using a custom CI/CD pipeline built with GitHub Actions.

* **Continuous Integration:** Automated multi-stage Docker builds on every push to the `main` branch to ensure environment stability.
* **Container Registry (AWS ECR):** GitHub Actions securely authenticates via IAM Least Privilege policies to push compiled images to a private Elastic Container Registry.
* **Production Deployment (AWS EC2):** A dedicated Ubuntu EC2 instance pulls the latest image from the ECR vault and restarts the FastAPI container. The server is secured via strict Security Group inbound rules and `.env` secrets are injected dynamically through the CI/CD pipeline tunnel.
