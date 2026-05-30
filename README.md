# Local Production-Grade RAG Pipeline on Kubernetes

A production-ready Retrieval-Augmented Generation (RAG) system engineered inside a local Kubernetes cluster environment. The pipeline ingests academic manuscripts from MongoDB, generates dense vector representations using a local embedding model, indexes them into Weaviate via gRPC, and runs localized streaming inference through Ollama.

## 🏗️ System Architecture
* **Inference Orchestration:** Python 3.12, LangChain, Ollama (Llama 3.2:3b)
* **Vector Database:** Weaviate V4 Cluster (HTTP/gRPC enabled)
* **NoSQL Metadata Store:** MongoDB Service
* **Containerization:** Kubernetes (kubectl), Docker Desktop Bridge

---

## 🚀 Deployment & Workflow Execution

1. Vector Schema Ingestion & Indexing
Run the indexing script inside the application deployment pod to purge old schemas, split text chunks, compute dense vectors via `all-MiniLM-L6-v2`, and batch-insert them into Weaviate:
```bash
kubectl exec -it deploy/rag-app-deployment -- python src/indexing.py

2. Run Live Interactive Shell
Execute the core engine loop to open the interactive RAG CLI terminal interface:
kubectl exec -it deploy/rag-app-deployment -- python src/pipeline.py

3. Run Automated Metrics Evaluation Suite
Validate system execution window tracking, Time-to-First-Token (TTFT), and database latency metrics:
kubectl exec -it deploy/rag-app-deployment -- python src/test_metrics.py