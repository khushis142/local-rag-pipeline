# Localized Cloud-Native RAG Pipeline on Kubernetes

An isolated, localized Retrieval-Augmented Generation (RAG) pipeline orchestrated entirely within a containerized Kubernetes environment. This repository serves as a deep-dive into cloud-native microservices, structural vector indexing, and deterministic context grounding for parsing academic and scientific research documents.

## 🏗️ System Architecture & Data Flow

The entire workflow executes locally on the host machine within an isolated cluster boundary:

1. **Ingestion:** Raw document components are extracted from a localized NoSQL instance (**MongoDB**).
2. **Text Chunking & Vectorization:** Text inputs are split via `RecursiveCharacterTextSplitter` and converted into 384-dimensional dense embeddings using an in-memory transformer model (**HuggingFace `all-MiniLM-L6-v2`**).
3. **gRPC Indexing & Retrieval:** Dense arrays are packed into transactional batches and indexed into a vector database (**Weaviate V4**) using high-speed, binary gRPC streaming connections.
4. **Contextual Inference:** Prompts are matched against vector properties, bundled into structural safety system constraints, and piped to a localized LLM (**Ollama Llama 3.2:3b**) using a `0.0` temperature coefficient to guarantee absolute determinism.

---

## 🛠️ Tech Stack & Component Scope

* **Orchestration:** Kubernetes (via Docker Desktop) — Manages isolated pod network topology, core internal DNS mapping, and container-to-host bridges.
* **Vector Database:** Weaviate V4 — Configured with an explicit data property schema and native gRPC endpoint streaming.
* **NoSQL Database:** MongoDB — Acts as the persistent metadata document repository.
* **Embeddings & Orchestration:** LangChain Community / HuggingFace Transformers.
* **Local Inference Node:** Ollama CLI Client (`llama3.2:3b`).

---

## 📁 Repository Structure

```text
local-rag-pipeline/
├── src/
│   ├── indexing.py      # Clears namespaces, defines V4 schemas, batches dense vectors to Weaviate
│   ├── pipeline.py      # Core RAG engine loop, global memory caching, and inference streaming
│   └── test_metrics.py  # Automated enterprise compliance, safety, and latency testing suite
├── .gitignore           # Prevents tracking runtime caches and local virtual environments
└── README.md            # Technical system documentation

## 🚀 Execution & Deployment Workflow
1. Synchronize Local Code to Cluster Node
To push configuration updates across your local development directory into the active container footprint, use the native Kubernetes file copy path:

kubectl cp src/indexing.py rag-app-deployment-7c64d7d9f9-86zkn:/app/src/indexing.py
kubectl cp src/pipeline.py rag-app-deployment-7c64d7d9f9-86zkn:/app/src/pipeline.py
kubectl cp src/test_metrics.py rag-app-deployment-7c64d7d9f9-86zkn:/app/src/test_metrics.py

2. Populate Schema & Execute Ingestion Pipeline
Run the database vectorizer script inside the container pod to clear existing data pools, build explicit schemas, calculate vector spaces, and run bulk batch operations:

kubectl exec -it rag-app-deployment-7c64d7d9f9-86zkn -- python src/indexing.py

3. Run the Automated Evaluation Suite
Trigger the regression testing harness to verify mathematical keyword grounding, hallucination guardrail thresholds, and system execution latency metrics:

kubectl exec -it rag-app-deployment-7c64d7d9f9-86zkn -- python src/test_metrics.py

## 📊 Evaluation Metrics & System Telemetry
The system was evaluated using an automated test matrix designed to isolate domain-specific retrieval capabilities against adversarial out-of-bounds queries.

| Regression Test Criteria | Vectorization Latency | Retrieval DB Latency (gRPC) | Time to First Token (TTFT) | Total Generation Window | Guardrail Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. In-Context Fact Retrieval** | `1630.25 ms` | `216.20 ms` | `16245.13 ms` | `22162.36 ms` | **`✅ PASSED`** (Context Grounded) |
| **2. Out-of-Bounds Adversarial Request** | `1684.95 ms` | `148.88 ms` | `10510.86 ms` | `11354.23 ms` | **`✅ PASSED`** (Refusal Triggered) |

## Telemetry Insights:

Sub-Second Vector Search: Weaviate V4 gRPC binary communication layers process semantic neighbor searches with exceptionally low latency overhead (148ms to 216ms).

Hardware Compute Bounds: The elevated Time-to-First-Token metrics (10.5s to 16.2s) pinpoint a hardware bottleneck: running localized, un-quantized text-generation weights on shared CPU allocations inside a local virtual container engine creates clear thread queuing.

## 🧠 Engineering Milestones & Debugging History

gRPC Auto-Schema Resolution: Fixed an explicit runtime query dropout error (Query call with protocol GRPC search failed with message no such prop with name 'title') by deprecating Weaviate auto-generation and declaring strict, typed structures using Property(name="content", data_type=DataType.TEXT) upon collection initialization.

Functional Scope Weight Caching: Eliminated high processing latency penalties by extracting the initialization of HuggingFaceEmbeddings out of the localized request loops and into the global module scope, keeping transformer weight tensors permanently warm in memory.

Sandbox Network Resolution: Overcame port deflection blockages by re-routing cross-network inference boundaries out of individual pod limits and targeting the host application loopback bridge via http://host.docker.internal:11434.

Git History Purification: Fixed push rejection limits (GH001: Large files detected) caused by tracking heavy PyTorch binaries (torch_cpu.dll). Used low-level Git file tree restructuring (git rm --cached) to scrub local commit history, pair dependencies with an organized .gitignore, and force a lightweight push strategy.