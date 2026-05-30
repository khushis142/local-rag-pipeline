from pyspark.sql import SparkSession
from pymongo import MongoClient
import json

def run_ingestion():
    print("--> Starting Local Spark Session...")
    # Initialize Spark with MongoDB Connector
    spark = SparkSession.builder \
        .appName("PipelineIngestion") \
        .master("local[*]") \
        .getOrCreate()

    # Read Raw Data
    #df = spark.read.json("data/arxiv_sample.json")
    df = spark.read.option("multiLine", "true").json("data/")
    print("--- EXAMINING REAL SPARK SCHEMA ---")
    df.printSchema()
    print("-----------------------------------")
    # Process/Clean Data (Filter out rows without abstracts)
    cleaned_df = df.filter(df.abstract.isNotNull())
    
    print(f"--> Processed {cleaned_df.count()} documents.")
    
    # Convert back to JSON strings to load into MongoDB
    records = [row.asDict() for row in cleaned_df.collect()]
    
    # Write to MongoDB
    #client = MongoClient("mongodb://localhost:27017/")
    # Changed from localhost to the Kubernetes service name
    client = MongoClient("mongodb://mongodb-service:27017/")
    db = client["research_db"]
    collection = db["reports"]
    
    # Avoid duplicates for our rerun cleanly
    collection.delete_many({}) 
    collection.insert_many(records)
    
    print("--> Data successfully synced to MongoDB repository.")
    spark.stop()

if __name__ == "__main__":
    run_ingestion()