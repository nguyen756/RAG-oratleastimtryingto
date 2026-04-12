
# Cloud-Native RAG Microservice & Semantic Cache 

## Overview
A full-stack, containerized Retrieval-Augmented Generation (RAG) system deployed on AWS. This architecture is designed to ingest, embed, and query highly specific domain data (currently configured for gaming mechanics) while prioritizing low-latency responses, cost optimization, and high availability.

The infrastructure is fully decoupled into a Node.js frontend and a Python/FastAPI backend, orchestrated via Docker Compose and deployed through a zero-touch GitHub Actions CI/CD pipeline.



*EIP and Instance currently being paused to save my wallet*


<img width="821" height="921" alt="RAG drawio" src="https://github.com/user-attachments/assets/777485d9-e77a-46ee-b60a-cc0e3256cc43" />


## Core Architecture & Features

### 1. Infrastructure as Code (IaC) & Zero-Trust Security
* **Terraform Provisioning:** AWS EC2 instances, EBS volumes, and Security Groups are entirely defined and deployed using Terraform HCL, ensuring reproducible and disposable cloud environments.
* **Observability Firewalls:** Configured Terraform to explicitly manage ingress rules, dynamically opening specific ports (4000, 9090) through the AWS Security Group to allow traffic to the Prometheus and Grafana monitoring stack.
* **SSL Termination & Proxy:** Implemented an Nginx reverse proxy with Let's Encrypt certificates to terminate HTTPS traffic. This acts as a gateway to drop unauthorized requests, preventing malicious bot swarms from scraping endpoints and draining LLM API quotas.

### 2. Dual-FAISS Semantic Caching 
To prevent redundant LLM API calls and drastically reduce user latency, this system implements an in-memory semantic caching layer.
* **Vector-Based Interception:** Uses a secondary, in-memory FAISS index (`IndexFlatL2`) to calculate the cosine similarity/distance of incoming user queries against previously asked questions.
* **Millisecond Resolution:** Cache hits bypass the Gemini API entirely, returning verified answers in ~8ms.
* **Automated Memory Management:** Implements an automated cache-flush protocol (500 query limit for now, and can be adjusted) to prevent out-of-memory (OOM) server crashes.

### 3. Agentic LLM Routing & Tool Use
The backend does not rely on a static prompt chain. Instead, it utilizes Google Gemini as a dynamic reasoning engine equipped with custom tool-calling capabilities.
* **Dynamic Query Routing:** The LLM evaluates the user's intent and autonomously triggers internal Python functions. 
* **Math & Logic Execution:** If a user asks a stat-based question (e.g., Attack/Cast Speed modifiers), the Agent triggers a deterministic `calculate_mscs` function rather than hallucinating math.
* **Vector Execution:** If the query requires game lore or mechanics, the Agent triggers the `general_question` tool to perform the FAISS L2 similarity search.

### 4. DevOps & Self-Healing Infrastructure
* **Automated CI/CD Pipeline:** GitHub Actions automatically builds and pushes multi-stage Docker images to AWS ECR on every main branch commit.
* **IaC Deployment via SCP:** Uses Secure Copy Protocol (SCP) within the GitHub Actions pipeline to transfer strict production configurations (`docker-compose.prod.yml`, Nginx rules) directly to the EC2 server, completely removing brittle inline bash scripts.
* **Load Tested & Fault Tolerant:** Validated architecture using Locust to simulate high-concurrency traffic (about 100+ simultaneous users). Engineered graceful degradation via Python `try/except` nets to catch upstream LLM rate-limit blocks (HTTP 429), resulting in a 0% server crash rate under heavy load.
* **Automated Garbage Collection:** The deployment pipeline includes automated `docker system prune` commands to clear dangling images and stopped containers, preventing EC2 hard drive saturation and timeout failures.

### 5. Custom Data Engineering & Ingestion
* **Stateful Volume Mounting:** FAISS indices and synchronization ledgers are hardcoded to absolute paths (`/data`) and mapped to physical AWS EC2 volumes. This ensures the database survives ephemeral Docker container reboots without data amnesia. 
* **Chunking:** Uses 2 different types of chunking. One is custom Regex targeting (`r"\|\s*#[^\s]+"`) via `PyMuPDF` to slice PDFs purely by semantic boundaries (`#blade-skills🗡` and such). The other one uses regular text-limit chunking.
* **Modular Web Scraping:** Includes preserved `BeautifulSoup4` pipelines to clean, normalize, and ingest raw HTML `bodyContent` for future domain expansion.

### 6. Observability & Monitoring
The system is instrumented with a full monitoring stack to observe server health, track LLM latency, and monitor API traffic.
* **Metrics Engine (`prometheus-fastapi-instrumentator`):** FastAPI natively exposes a `/metrics` endpoint, broadcasting application state.
* **Prometheus:** Scrapes and stores the backend hardware and traffic state every 5 seconds.
* **Grafana:** Visualizes the Prometheus data via custom dashboards to track memory limits and prevent OOM failures in real-time. 

## Tech Stack
* **DevOps / Cloud:** AWS (EC2, ECR, IAM), Terraform, Docker, Docker Compose, GitHub Actions, Nginx
* **Backend:** Python 3.12+, FastAPI, Uvicorn
* **Frontend:** Node.js v24, Express, Handlebars (Deployed via Render)
* **ML / Data:** FAISS (CPU), SentenceTransformers, Gemini API, PyMuPDF, BeautifulSoup4
* **Observability:** Prometheus, Grafana

---

## Environment Setup & Usage

### Local Development (Testing & Building)
Use these instructions to run the architecture in a local sandbox without affecting the live server.

1. Clone the repository.
2. Create a `.env` file in the root directory and add your keys: 
   ```env
   GEMINI_API_KEY=your_key_here
   GRAFANA_PASSWORD=your_password_here
   ```
3. Spin up the decoupled environment (using the local `docker-compose.yml`):
   ```bash
   docker compose up --build
   ```
4. Access the frontend UI at `http://localhost:3000` and test the backend health via `http://localhost/docs`
5. **Database Maintenance:** If you need to wipe the FAISS database and the hash ledger to ingest fresh documents, run the provided cleanup script before rebuilding:
   ```bash
   ./clean.sh
   ```

### Production Deployment (AWS)
The live infrastructure is strictly managed via GitHub Actions and Terraform.

* **Triggering a Deployment:** Pushing any code to the `main` branch automatically triggers the CI/CD pipeline. The pipeline will pass tests, build the ECR image, transfer the `docker-compose.prod.yml` via SCP, and deploy the new stack to the EC2 server with zero downtime.
* **Live Architecture Endpoints:**
  * **Secure Backend API:** `https://gwasiodmzol.shop`
  * **Observability Dashboard (Grafana):** `http://<elastic-ip>:4000` (Requires authentication)
* Observability Dashboard (Grafana): http://<elastic-ip>:4000 (Requires authentication)

