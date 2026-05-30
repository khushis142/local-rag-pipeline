import weaviate
from pymongo import MongoClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from weaviate.classes.data import DataObject

def run_indexing():
    mongo_client = MongoClient("mongodb://mongodb-service:27017/")
    db = mongo_client["research_db"]
    reports = list(db["reports"].find({}))

    client = weaviate.connect_to_custom(
        http_host="weaviate-service", http_port=8080, http_secure=False,
        grpc_host="weaviate-service", grpc_port=50051, grpc_secure=False
    )

    try:
        if client.collections.exists("ResearchReport"):
            client.collections.delete("ResearchReport")

        client.collections.create(
            name="ResearchReport",
            description="A collection of academic and industry research papers"
        )
        
        collection = client.collections.get("ResearchReport")

        print("--> Loading Embedding Model (all-MiniLM-L6-v2)...")
        embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        print("--> Generating Embeddings and Chunking...")
        
        # Accumulate ALL objects across all documents to insert them in batches
        data_objects = []

        for report in reports:
            chunks = text_splitter.split_text(report["abstract"])
            
            for chunk in chunks:
                # 1. Compute vector embedding for this specific text chunk
                vector = embeddings_model.embed_query(chunk)
                
                # 2. Append the structured DataObject to our batch list
                data_objects.append(
                    DataObject(
                        properties={
                            "title": report.get("title"),
                            "content": chunk,  # Maps cleanly to the pipeline query key
                            "category": report.get("category")
                        },
                        vector=vector  # Explicitly assigns the float list as this chunk's vector
                    )
                )

        # 3. Insert everything cleanly using a unified v4 batch execution
        if data_objects:
            response = collection.data.insert_many(data_objects)
            if response.has_errors:
                print(f"--> Batch insertion had issues: {response.errors}")
            else:
                print(f"--> Success! Total Vectorized Records in Weaviate: {len(data_objects)}")
                
    finally:
        client.close()

if __name__ == "__main__":
    run_indexing()