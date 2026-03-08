# Cloud-Native RAG Microservice & Semantic Cache 


## Overview
A full-stack, containerized Retrieval-Augmented Generation (RAG) system deployed on AWS. This architecture is designed to ingest, embed, and query highly specific domain data (currently configured for gaming mechanics) while prioritizing low-latency responses, cost optimization, and high availability.

The infrastructure is fully decoupled into a Node.js frontend and a Python/FastAPI backend, orchestrated via Docker Compose and deployed through a zero-touch GitHub Actions CI/CD pipeline.

## Core Architecture & Features

### 1. Zero-Trust Security & API Protection
* **Reverse Proxy:** Implemented an Nginx reverse proxy to shield the FastAPI backend from direct public internet traffic. This acts as a gateway to drop unauthorized requests, preventing malicious bot swarms from scraping the endpoints and draining LLM API quotas.

### 2. Dual-FAISS Semantic Caching 
To prevent redundant LLM API calls and drastically reduce user latency, this system implements an in-memory semantic caching layer.
* **Vector-Based Interception:** Uses a secondary, in-memory FAISS index (`IndexFlatL2`) to calculate the cosine similarity/distance of incoming user queries against previously asked questions.
* **Millisecond Resolution:** Cache hits bypass the Gemini API entirely, returning verified answers.
* **Automated Memory Management:** Implements an automated cache-flush protocol (1,000 query limit) to prevent out-of-memory (OOM) server crashes.

### 3. DevOps & Self-Healing Infrastructure
* **Automated CI/CD Pipeline:** GitHub Actions automatically builds and pushes multi-stage Docker images to AWS ECR on every main branch commit.
* **AWS EC2 Deployment:** The production server dynamically pulls the latest images and injects `.env` secrets via IAM Least Privilege policies.
* **Automated Garbage Collection:** The deployment pipeline includes automated `docker system prune` commands to clear dangling images and stopped containers, preventing EC2 hard drive saturation and timeout failures.
* **Self-Healing Containers:** Configured with active Docker `healthcheck` probing the FastAPI `/health` endpoint. The orchestrator automatically tears down and reboots zombie containers if the application freezes, ensuring 24/7 uptime without manual intervention.

### 4. Custom Data Engineering & Ingestion
* **Stateful Volume Mounting:** FAISS indices and synchronization ledgers are hardcoded to absolute paths (`/data`) and mapped to physical AWS EC2 volumes. This ensures the database survives ephemeral Docker container reboots without data amnesia. 
* **Precision Chunking:** Bypasses standard, error-prone character-limit chunking. Implements custom Regex targeting (`r"\|\s*#[^\s]+"`) via `PyMuPDF` to slice PDFs purely by semantic boundaries (`#blade-skills🗡` and such).
* **Modular Web Scraping:** Includes preserved `BeautifulSoup4` pipelines to clean, normalize, and ingest raw HTML `bodyContent` for future domain expansion.

## Tech Stack
* **DevOps / Cloud:** AWS (EC2, ECR, IAM), Docker, Docker Compose, GitHub Actions, Nginx
* **Backend:** Python 3.12+, FastAPI, Uvicorn
* **Frontend:** Node.js v24, Express, Handlebars (Deployed via Render)
* **ML / Data:** FAISS (CPU), SentenceTransformers, Gemini API, PyMuPDF, BeautifulSoup4

## Architectural Roadmap (Next Steps)
* **Metadata Pre-Filtering:** Upgrading the current ingestion pipeline to inject structured JSON tags into the FAISS vectors. This will allow an LLM-driven "bouncer" to pre-filter database chunks by hard attributes (e.g., weapon type, level requirement) before the semantic search begins, eliminating cross-contamination in high-`top_k` searches.

## Quick Start (Local Development)

1. Clone the repository.
2. Create a `.env` file in the root directory:  and put `GEMINI_API_KEY=` into
3. Spin up the decoupled environment and the Nginx proxy:
   ```bash
   docker compose up --build
4. Access the frontend UI at http://localhost:3000 and test the backend health via http://localhost/docs
5. Database Maintenance: If you need to wipe the FAISS database and the hash ledger to ingest fresh documents, run the provided cleanup script before rebuilding:
   ```bash
      .clean/sh