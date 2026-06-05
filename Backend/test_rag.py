from src.retriever import SecurityRetriever
import os

# Lower threshold to see what the actual scores are
os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.3"

retriever = SecurityRetriever()

# The pipeline sends queries like this:
query_text = "SQL Injection vulnerability in python"
print(f"Querying: '{query_text}'")

results = retriever.query_with_metadata(query_text)

print("no_match:", results.no_match)
for i, r in enumerate(results.chunks, 1):
    d = r.to_dict()
    print(f"\n--- Chunk {i} ---")
    print(f"Score:    {d['score']}")
    print(f"Source:   {d['source']}")
    print(f"Severity: {d['severity']}")
    print(f"Text:     {d['text'][:150]}...")
