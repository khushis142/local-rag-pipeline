import weaviate
import time
from langchain_community.embeddings import HuggingFaceEmbeddings
import ollama
import os
os.environ["OLLAMA_HOST"] = "http://host.docker.internal:11434"

def query_rag_system(user_query: str):
    start_time = time.time()
    
    # 1. Generate Query Vector
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    query_vector = embeddings_model.embed_query(user_query)
    
    # 2. Semantic Search over Weaviate
    #client = weaviate.connect_to_local()
    # Connect to the cluster service name
    client = weaviate.connect_to_custom(
        http_host="weaviate-service",
        http_port=8080,
        http_secure=False,
        grpc_host="weaviate-service",
        grpc_port=50051,
        grpc_secure=False
    )
    collection = client.collections.get("ResearchReport")
    
    response = collection.query.near_vector(
        near_vector=query_vector,
        limit=2, # Keep context small and efficient
        return_properties=["title", "content"]
    )
    client.close()
    
    # 3. Compile Context
    context_snippets = []
    for obj in response.objects:
        context_snippets.append(f"Document [{obj.properties['title']}]: {obj.properties['content']}")
    
    context_str = "\n\n".join(context_snippets)
    
    # 4. Prompt Engineering (Mimicking corporate governance & tone constraints)
    system_prompt = (
    "You are an advanced AI academic research assistant specializing in Computer Science and Artificial Intelligence. "
    "Your task is to answer user queries using ONLY the provided scientific paper abstracts below. "
    "If the answer cannot be confidently deduced from the given context, state clearly that you do not possess "
    "the academic information. Maintain a highly precise, scholarly, objective, and analytical tone."
    )
    
    user_prompt = f"CONTEXT:\n{context_str}\n\nUSER QUERY: {user_query}\n\nANSWER:"
    
    # 5. Local LLM Generation via Ollama
    print("\n--> Fetching Answer from Local LLaMA Stack...")
    ollama_response = ollama.generate(
        model='llama3.2:3b', # or your selected model variant
        system=system_prompt,
        prompt=user_prompt,
        options={"temperature": 0.0} # Absolute deterministic output for accuracy
    )
    
    elapsed_time = time.time() - start_time
    
    print("\n=== SYSTEM ANSWER ===")
    print(ollama_response['response'])
    print("=====================")
    print(f"Metrics: Query executed cleanly in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    print("Welcome to the arXiv RAG Prototype.")
    while True:
        query = input("\nEnter your query (or type 'exit'): ")
        if query.lower() == 'exit':
            break
        query_rag_system(query)