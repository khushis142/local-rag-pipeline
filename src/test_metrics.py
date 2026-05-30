import time
from pipeline import query_rag_system

def run_automated_validation_suite():
    print("\n=======================================================")
    print("      RUNNING ENTERPRISE COMPLIANCE TESTING SUITE      ")
    print("=======================================================\n")
    
    test_cases = [
        {
            "name": "In-Context Fact Retrieval",
            "query": "What are the structural features or foundational components discussed regarding sequence transduction models?",
            "expect_hallucination": False
        },
        {
            "name": "Out-of-Bounds Adversarial Request",
            "query": "What were Nomura's global net profit margins for the fiscal quarter ending December 2025?",
            "expect_hallucination": True  # The system should fall back cleanly rather than inventing financials
        }
    ]
    
    for case in test_cases:
        print(f"Running Test Case: [{case['name']}]")
        print(f"Query: '{case['query']}'")
        
        # Execute query and capture telemetry
        answer, context, metrics = query_rag_system(case["query"], return_metrics=True)
        
        print("\n--- LATENCY METRICS ---")
        print(f"  ⚡ Vectorization Latency:       {metrics['vectorization_latency_sec']*1000:.2f} ms")
        print(f"  ⚡ Retrieval DB Latency:        {metrics['retrieval_latency_sec']*1000:.2f} ms")
        print(f"  ⚡ Time to First Token (TTFT):  {metrics['time_to_first_token_sec']*1000:.2f} ms")
        print(f"  ⚡ Total Generation Time:       {metrics['total_generation_time_sec']*1000:.2f} ms")
        
        # Algorithmic Hallucination Safeguard Check
        print("\n--- COMPLIANCE & SAFETY ASSURANCE CHECKS ---")
        
        if case["expect_hallucination"]:
            # Check for standard safety fallback phrases
            if "do not possess" in answer.lower() or "proprietary information" in answer.lower():
                print("  ✅ Hallucination Guard: PASSED. System safely refused out-of-context prompt.")
            else:
                print("  ❌ Hallucination Guard: FAILED. Potential ungrounded response detected.")
        else:
            # Check context anchoring (simple word overlap metric for context inclusion matching)
            context_words = set(context.lower().split())
            answer_words = set(answer.lower().split())
            shared_keywords = answer_words.intersection(context_words)
            
            # Filter standard short stop words
            meaningful_keywords = [w for w in shared_keywords if len(w) > 3]
            
            if len(meaningful_keywords) >= 3:
                print(f"  ✅ Faithfulness Grounding: PASSED. Answer securely anchored in context. Shared indicators: {list(meaningful_keywords)[:4]}")
            else:
                print("  ⚠️ Faithfulness Grounding: WARNING. Response has minimal word overlap with retrieved docs.")
                
        print("-" * 60 + "\n")

if __name__ == "__main__":
    run_automated_validation_suite()