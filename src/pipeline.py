import weaviate
import time
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from ollama import Client

# Point out of cluster back to host machine server configuration
#os.environ["OLLAMA_HOST"] = "http://host.docker.internal:11434"

# 1. OPTIMIZATION: Instantiate ONCE at module load time (Global Scope)
print("--> Warm-loading local embedding model into memory...")
GLOBAL_EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def query_rag_system(user_query: str, return_metrics=False):
    metrics = {}
    #ollama_client = Client(host="http://ollama-service:11434")
    ollama_client = Client(host="http://host.docker.internal:11434")
    # 1. Vectorization Latency Execution / Generate Query Vector
    start_vec = time.perf_counter()
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    #query_vector = embeddings_model.embed_query(user_query)
    query_vector = GLOBAL_EMBEDDINGS_MODEL.embed_query(user_query)
    metrics["vectorization_latency_sec"] = time.perf_counter() - start_vec
    
    # 2. Retrieval Latency Execution
    start_ret = time.perf_counter()

    # Semantic Search over Weaviate
    #client = weaviate.connect_to_local()
    # Connect to the cluster service name
    client = weaviate.connect_to_custom(
        http_host="weaviate-service", http_port=8080, http_secure=False,
        grpc_host="weaviate-service", grpc_port=50051, grpc_secure=False
    )
    collection = client.collections.get("ResearchReport")
    response = collection.query.near_vector(near_vector=query_vector, limit=2, return_properties=["title", "content"]) # Keep context small and efficient
    client.close()
    metrics["retrieval_latency_sec"] = time.perf_counter() - start_ret
    
    # Compile text context chunks
    context_snippets = [f"Doc [{obj.properties['title']}]: {obj.properties['content']}" for obj in response.objects]
    context_str = "\n\n".join(context_snippets)
    
    # Prompt Engineering (Mimicking corporate governance & tone constraints)
    system_prompt = (
        "You are an AI research assistant. Answer the user query using ONLY the provided context. "
        "If the answer cannot be confidently deduced, state 'I do not possess the proprietary information.' "
        "Do not invent facts outside the text."
    )
    user_prompt = f"CONTEXT:\n{context_str}\n\nUSER QUERY: {user_query}\n\nANSWER:"
    
    # 3. Token Generation Latency Tracking (Time to First Token)
    start_gen = time.perf_counter()
    stream = ollama_client.generate(model='llama3.2:3b', system=system_prompt, prompt=user_prompt, options={"temperature": 0.0}, stream=True) # Absolute deterministic output for accuracy
    
    first_token_received = False
    full_response = ""
    time_to_first_token = 0.0
    
    for chunk in stream:
        if not first_token_received:
            time_to_first_token = time.perf_counter() - start_gen
            first_token_received = True
        full_response += chunk['response']
        
    metrics["time_to_first_token_sec"] = time_to_first_token
    metrics["total_generation_time_sec"] = time.perf_counter() - start_gen

    if return_metrics:
        return full_response, context_str, metrics
    return full_response, context_str

if __name__ == "__main__":
    print("\n--- Live RAG Cluster Shell ---")
    while True:
        q = input("\nEnter query (or type 'exit'): ")
        if q.lower() == 'exit': break
        ans, ctx, met = query_rag_system(q, return_metrics=True)
        print(f"\n[Answer]: {ans}")
        print(f"\n[Metrics Breakdown]:\n - Vectorization Time: {met['vectorization_latency_sec']:.4f}s\n - Retrieval Database Time: {met['retrieval_latency_sec']:.4f}s\n - Time to First Token (TTFT): {met['time_to_first_token_sec']:.4f}s\n - Total Generation Window: {met['total_generation_time_sec']:.4f}s")

        # === ADD THIS DEBUG LINE HERE ===
        print(f"\n[DEBUG - Context Fed to LLM]:\n{ctx}\n-------------------")
        
        print(f"\n[Answer]: {ans}")
        print(f"\n[Metrics Breakdown]...")