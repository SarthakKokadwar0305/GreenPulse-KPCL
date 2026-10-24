# 🚀 GreenPulse AI - Docker Deployment Guide

This guide walks you through deploying the complete **GreenPulse AI** production stack (Next.js Frontend, FastAPI Backend with ML Models, and Qdrant Vector DB) using **Docker Compose**.

---

## 🏗️ Architecture

```
                      ┌────────────────────────────┐
                      │    Client Browser          │
                      │  http://localhost:3000     │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                 Docker Bridge Network                  │
       │                                                        │
       │   ┌────────────────────┐      ┌────────────────────┐   │
       │   │   frontend         │      │   backend          │   │
       │   │   (Next.js 16)     │─────▶│   (FastAPI + ML)   │   │
       │   │   Port: 3000       │      │   Port: 8000       │   │
       │   └────────────────────┘      └─────────┬──────────┘   │
       │                                         │              │
       │                                         ▼              │
       │                               ┌────────────────────┐   │
       │                               │   qdrant           │   │
       │                               │   (Vector DB)      │   │
       │                               │   Port: 6333       │   │
       │                               └────────────────────┘   │
       └────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

1. **Docker Desktop** (for Windows / macOS) or **Docker Engine + Docker Compose** (for Linux).
   - Ensure Docker is running: `docker --version` and `docker compose version`
2. **RAM**: Minimum 4 GB RAM allocated to Docker.

---

## ⚡ Quick Start (1-Command Launch)

From the root directory (`KPCL_Hackathon`):

```bash
docker compose up --build -d
```

Docker will:
1. Pull the official **Qdrant Vector DB** image (`qdrant/qdrant:v1.12.0`).
2. Build the **FastAPI Backend** container with all ML models and dependencies.
3. Build the **Next.js 16 Frontend** multi-stage production container.
4. Mount persistent volumes for vector storage and uploaded documents.
5. Launch all three services on their designated ports.

---

## 🌐 Accessing the Services

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:3000](http://localhost:3000) | Full GreenPulse AI Dashboard, Digital Twin, Analytics & Copilot |
| **Backend API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger UI for all 24+ REST endpoints |
| **Backend Health** | [http://localhost:8000/health](http://localhost:8000/health) | System health & model status |
| **Qdrant Dashboard** | [http://localhost:6333/dashboard](http://localhost:6333/dashboard) | Web interface to inspect vector collections and embeddings |

---

## 🛠️ Management Commands

### Check Running Containers
```bash
docker compose ps
```

### View Live Logs
```bash
# View logs from all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f qdrant
```

### Stop the Containers
```bash
# Stop containers without deleting data
docker compose stop

# Stop and remove containers (data in persistent volumes is preserved)
docker compose down

# Stop and delete persistent volumes (resets vector DB and uploads)
docker compose down -v
```

---

## ☁️ Deploying to a Cloud VPS (DigitalOcean / AWS / GCP / Azure)

1. **Launch an Ubuntu 22.04 / 24.04 VM** (e.g., DigitalOcean Droplet with 4GB RAM or AWS EC2 `t3.medium`).
2. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
3. **Clone your repository**:
   ```bash
   git clone https://github.com/SarthakKokadwar0305/GreenPulse-KPCL.git
   cd GreenPulse-KPCL
   ```
4. **Launch the stack**:
   ```bash
   docker compose up --build -d
   ```
5. Access your server via `http://<SERVER_PUBLIC_IP>:3000`.
