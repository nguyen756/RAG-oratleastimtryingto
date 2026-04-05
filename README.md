# Cloud-Native RAG Microservice & Semantic Cache 

## Overview
A full-stack, containerized Retrieval-Augmented Generation (RAG) system deployed on AWS. This architecture is designed to ingest, embed, and query highly specific domain data (currently configured for gaming mechanics) while prioritizing low-latency responses, cost optimization, and high availability.

The infrastructure is fully decoupled into a Node.js frontend and a Python/FastAPI backend, orchestrated via Docker Compose and deployed through a zero-touch GitHub Actions CI/CD pipeline.



*EIP and Instance currently being paused to save my wallet*



## Core Architecture & Features

### 1. Infrastructure as Code (IaC) & Zero-Trust Security
* **Terraform Provisioning:** AWS EC2 instances, EBS volumes, and Security Groups are entirely defined and deployed using Terraform HCL, ensuring reproducible and disposable cloud environments.
* **Observability Firewalls:** Configured Terraform to explicitly manage ingress rules, dynamically opening specific ports (4000, 9090) through the AWS Security Group to allow traffic to the Prometheus and Grafana monitoring stack.
* **SSL Termination & Proxy:** Implemented an Nginx reverse proxy with Let's Encrypt certificates to terminate HTTPS traffic. This acts as a gateway to drop unauthorized requests, preventing malicious bot swarms from scraping endpoints and draining LLM API quotas.

### 2. Dual-FAISS Semantic Caching 
To prevent redundant LLM API calls and drastically reduce user latency, this system implements an in-memory semantic caching layer.
* **Vector-Based Interception:** Uses a secondary, in-memory FAISS index (`IndexFlatL2`) to calculate the cosine similarity/distance of incoming user queries against previously asked questions.
* **Millisecond Resolution:** Cache hits bypass the Gemini API entirely, returning verified answers.
* **Automated Memory Management:** Implements an automated cache-flush protocol (1,000 query limit) to prevent out-of-memory (OOM) server crashes.

### 3. DevOps & Self-Healing Infrastructure
* **Automated CI/CD Pipeline:** GitHub Actions automatically builds and pushes multi-stage Docker images to AWS ECR on every main branch commit.
* **IaC Deployment via SCP:** Uses Secure Copy Protocol (SCP) within the GitHub Actions pipeline to transfer strict production configurations (`docker-compose.prod.yml`, Nginx rules) directly to the EC2 server, completely removing brittle inline bash scripts.
* **Automated Garbage Collection:** The deployment pipeline includes automated `docker system prune` commands to clear dangling images and stopped containers, preventing EC2 hard drive saturation and timeout failures.
* **Self-Healing Containers:** Configured with active Docker `healthcheck` probing the FastAPI `/health` endpoint. The orchestrator automatically tears down and reboots zombie containers if the application freezes, ensuring 24/7 uptime without manual intervention.

### 4. Custom Data Engineering & Ingestion
* **Stateful Volume Mounting:** FAISS indices and synchronization ledgers are hardcoded to absolute paths (`/data`) and mapped to physical AWS EC2 volumes. This ensures the database survives ephemeral Docker container reboots without data amnesia. 
* **Chunking:** Uses 2 different types of chunking. One is custom Regex targeting (`r"\|\s*#[^\s]+"`) via `PyMuPDF` to slice PDFs purely by semantic boundaries (`#blade-skills🗡` and such). The other one uses regular text-limit chunking.
* **Modular Web Scraping:** Includes preserved `BeautifulSoup4` pipelines to clean, normalize, and ingest raw HTML `bodyContent` for future domain expansion.

### 5. Observability & Monitoring
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
2. Create a `.env` file in the root directory and add your key: `GEMINI_API_KEY=your_key_here`
`GRAFANA_PASSWORD=your_password_here`
3. Spin up the decoupled environment (using the local `docker-compose.yml`):
   ```bash
   docker compose up --build
4. Access the frontend UI at http://localhost:3000 and test the backend health via http://localhost/docs

5. Database Maintenance: If you need to wipe the FAISS database and the hash ledger to ingest fresh documents, run the provided cleanup script before rebuilding:

   ```bash
   ./clean.sh


## Production Deployment (AWS)
The live infrastructure is strictly managed via GitHub Actions and Terraform.

* Triggering a Deployment: Pushing any code to the main branch automatically triggers the CI/CD pipeline. The pipeline will pass tests, build the ECR image, transfer the docker-compose.prod.yml via SCP, and deploy the new stack to the EC2 server with zero downtime.

* Live Architecture Endpoints:

* Secure Backend API: **https://gwasiodmzol.shop**

* Observability Dashboard (Grafana): http://<elastic-ip>:4000 (Requires authentication)

