# query format:
# metadata info -
# 1. client id
#
# nl query
# context: This is breaking in this service in this env
# output: relevant chunks
# llm will use info found in these chunks to form a proper answer to the user's question

from supabase import create_client
from ingestion.embedder import generate_embedding
import os
from dotenv import load_dotenv

load_dotenv()

def retrieve_knowledge_chunks(query: str, client_id: str = None, doc_types: list = None, 
                              match_threshold: float = 0.5, match_count: int = 5):
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    query_embedding = generate_embedding(query)
    
    params = {
        "query_embedding": query_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count
    }
    
    if client_id:
        params["filter_client_id"] = client_id
    
    if doc_types:
        params["filter_doc_types"] = doc_types
    
    result = supabase.rpc("match_knowledge_chunks", params).execute()
    
    if not result.data:
        return []
    
    return result.data


if __name__ == "__main__":

    # HarborView Hotels 
    client_uuid = "dd23437f-7ea7-4c46-8beb-4e2b4e555651"  
    
    incident_context = """
    HarborView Hotels P1 Incident - StayEase PMS Connectivity Issues
    
    Environment Details:
    - Client: HarborView Hotels (ACC-1009)
    - Affected System: StayEase PMS
    - Impact: 8 out of 12 hotel properties unable to process check-ins/check-outs
    - Time: Peak check-in period (2:00 PM - 4:00 PM Singapore time)
    - Error Pattern: Intermittent database connection timeouts to SQL Server
    - Recent Changes: AWS RDS maintenance window completed 2 hours ago
    - Business Impact: Guests waiting in lobby, revenue loss from delayed check-ins
    """
    
    print("=" * 60)
    print("HARBORVIEW HOTELS - INCIDENT RETRIEVAL SAMPLE")
    print("=" * 60)
    print(f"Incident Context: {incident_context}")
    print("=" * 60)
    
    # Query 1: Database connectivity issues for PMS
    print("\n[Query 1] Database connectivity issues for StayEase PMS...")
    results = retrieve_knowledge_chunks(
        query="StayEase PMS database connection timeout SQL Server RDS connectivity issues",
        client_id=client_uuid,
        doc_types=["cod", "runbook"],
        match_threshold=0.5,
        match_count=5
    )
    
    print(f"Found {len(results)} relevant chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"  - Similarity: {chunk['similarity']:.3f}")
        print(f"  - Document Type: {chunk['doc_type']}")
        print(f"  - Document ID: {chunk['document_id']}")
        print(f"  - Client ID: {chunk['client_id']}")
        print(f"  - Chunk Text: {chunk['chunk_text'][:200]}...")
        if chunk.get('metadata'):
            print(f"  - Metadata: {chunk['metadata']}")
    
    # Query 2: AWS RDS troubleshooting specific to hospitality
    print("\n" + "=" * 60)
    print("[Query 2] AWS RDS SQL Server troubleshooting for hospitality...")
    results = retrieve_knowledge_chunks(
        query="AWS RDS SQL Server timeout connection issues hospitality PMS",
        client_id=client_uuid,
        doc_types=["runbook"],
        match_threshold=0.4,
        match_count=3
    )
    
    print(f"Found {len(results)} runbook chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"  - Similarity: {chunk['similarity']:.3f}")
        print(f"  - Chunk Text: {chunk['chunk_text'][:150]}...")
    
    # Query 3: Escalation procedures for P1 incidents
    print("\n" + "=" * 60)
    print("[Query 3] P1 incident escalation procedures for HarborView...")
    results = retrieve_knowledge_chunks(
        query="P1 incident escalation HarborView Hotels emergency procedures guest-facing outage",
        client_id=client_uuid,
        doc_types=["cod"],
        match_threshold=0.5,
        match_count=3
    )
    
    print(f"Found {len(results)} escalation procedure chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"  - Similarity: {chunk['similarity']:.3f}")
        print(f"  - Chunk Text: {chunk['chunk_text'][:150]}...")
    
    # Query 4: Network connectivity and SD-WAN issues
    print("\n" + "=" * 60)
    print("[Query 4] SD-WAN connectivity issues affecting hotel properties...")
    results = retrieve_knowledge_chunks(
        query="SD-WAN connectivity hotel properties network outage property failover",
        client_id=client_uuid,
        doc_types=["cod", "runbook"],
        match_threshold=0.5,
        match_count=4
    )
    
    print(f"Found {len(results)} network connectivity chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"  - Similarity: {chunk['similarity']:.3f}")
        print(f"  - Chunk Text: {chunk['chunk_text'][:150]}...")
    
    print("\n" + "=" * 60)
    print("INCIDENT RETRIEVAL COMPLETE")
    print("=" * 60)