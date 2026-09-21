# Ingestion pipeline for Lambda
# Expected to run every week to ingest updated info into the KB
from ingestion.read_coa import ReadCoA
from ingestion.chunker import chunk_by_sections, extract_section_metadata
from ingestion.embedder import generate_embedding, generate_embeddings_batch
import logging
import os
import json
import hashlib
import requests

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def ingest_cod_documents(supabase, folder_id: str):
    logger.info("Starting CoD document ingestion...")
    
    coa_reader = ReadCoA()
    
    try:
        logger.info(f"Fetching PDFs from Google Drive folder: {folder_id}")
        documents = coa_reader.read_pdfs_from_folder(folder_id)
        logger.info(f"Successfully fetched {len(documents)} documents from Google Drive")
        
        total_chunks = 0
        skipped_documents = 0
        
        for document in documents:
            document_id = document["file_id"]
            document_name = document["file_name"]
            document_text = document["text"]

            account_id = document_name.split("_")[0]  # ACC-####
            
            logger.info(f"Processing document: {document_name} (account_id: {account_id})")
            
            client_result = supabase.table("clients").select("id").eq("account_id", account_id).execute()
            
            if not client_result.data:
                logger.warning(f"Client with account_id {account_id} not found in database. Skipping document {document_name}")
                skipped_documents += 1
                continue
            
            client_uuid = client_result.data[0]["id"]
            logger.debug(f"Found client UUID: {client_uuid}")
            
            doc_metadata = extract_section_metadata(document_text)
            doc_metadata["extraction_date"] = logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
            
            content_hash = hashlib.sha256(document_text.encode()).hexdigest()
            
            chunks = chunk_by_sections(document_text, doc_metadata)
            logger.info(f"Document {document_name}: extracted {len(chunks)} chunks")
            
            document_result = supabase.table("kb_documents").insert({
                "client_id": client_uuid,
                "doc_type": "cod",
                "source_ref": document_id,
                "title": document_name,
                "content_hash": content_hash,
                "metadata": doc_metadata
            }).execute()
            
            document_uuid = document_result.data[0]["id"]
            logger.debug(f"Created document record with UUID: {document_uuid}")
            
            if chunks:
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = generate_embeddings_batch(chunk_texts)
                
                chunk_records = []
                for i, chunk in enumerate(chunks):
                    chunk_records.append({
                        "document_id": document_uuid,
                        "client_id": client_uuid,
                        "doc_type": "cod",
                        "chunk_index": chunk["metadata"]["chunk_index"],
                        "chunk_text": chunk["text"],
                        "metadata": chunk["metadata"],
                        "embedding": embeddings[i]
                    })
                    
                    logger.debug(f"Chunk {chunk['metadata']['chunk_index']}: section={chunk['metadata'].get('section', 'N/A')}, "
                                f"subsection={chunk['metadata'].get('subsection', 'N/A')}, "
                                f"length={len(chunk['text'])} chars")
                
                supabase.table("kb_embeddings").insert(chunk_records).execute()
                logger.info(f"Inserted {len(chunk_records)} chunks into kb_embeddings")
                total_chunks += len(chunk_records)
        
        logger.info(f"CoD ingestion completed. Total chunks inserted: {total_chunks}, Documents skipped: {skipped_documents}")
        
    except Exception as e:
        logger.error(f"Error during CoD ingestion: {str(e)}")
        raise


def ingest_runbooks(supabase):
    logger.info("Starting runbook ingestion...")
    
    wiki_url = os.environ.get("WIKI_URL")
    if not wiki_url:
        logger.error("WIKI_URL is not set in environment variables")
        return
    
    try:
        # Fetch all runbooks from the wiki API
        # Remove trailing slash from wiki_url if present
        wiki_url = wiki_url.rstrip('/')
        logger.info(f"Fetching runbooks from wiki API: {wiki_url}/api/runbook")
        runbooks_url = f"{wiki_url}/api/runbook"
        response = requests.get(runbooks_url)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch runbooks from wiki API: {response.status_code}")
            return
        
        grouped_runbooks = response.json()
        logger.info(f"Successfully fetched runbooks from {len(grouped_runbooks)} clients")
        
        total_chunks = 0
        skipped_runbooks = 0
        
        for company_name, runbooks in grouped_runbooks.items():
            logger.info(f"Processing runbooks for client: {company_name}")
            
            for runbook_ref in runbooks:
                runbook_reference = runbook_ref["runbook_reference"]
                
                # Get client_id from nested client object
                client_id = runbook_ref.get("client", {}).get("id")
                if not client_id:
                    logger.warning(f"Skipping runbook {runbook_reference} - missing client_id")
                    skipped_runbooks += 1
                    continue
                
                logger.info(f"Processing runbook: {runbook_reference} (client_id: {client_id})")
                
                try:
                    logger.debug(f"Fetching runbook data from API: {wiki_url}/api/runbook/{runbook_reference}")
                    runbook_url = f"{wiki_url}/api/runbook/{runbook_reference}"
                    runbook_response = requests.get(runbook_url)
                    
                    if runbook_response.status_code != 200:
                        logger.error(f"Failed to fetch runbook {runbook_reference}: {runbook_response.status_code}")
                        skipped_runbooks += 1
                        continue
                    
                    runbook_data = runbook_response.json()
                    
                    runbook_text = structure_runbook_text(runbook_data)
                    logger.debug(f"Structured runbook text length: {len(runbook_text)} characters")
                    
                    runbook_metadata = {
                        "runbook_id": runbook_data.get("runbook_id"),
                        "title": runbook_data.get("title"),
                        "client": runbook_data.get("client"),
                        "industry": runbook_data.get("industry"),
                        "account_id": runbook_data.get("account_id"),
                        "severity": runbook_data.get("severity"),
                        "affected_systems": runbook_data.get("affected_systems", []),
                        "services": runbook_data.get("services", []),
                        "estimated_resolution_time": runbook_data.get("estimated_resolution_time"),
                        "last_updated": runbook_data.get("last_updated"),
                        "extraction_date": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
                    }
                    
                    content_hash = hashlib.sha256(runbook_text.encode()).hexdigest()
                    
                    chunks = chunk_by_sections(runbook_text, runbook_metadata)
                    logger.info(f"Runbook {runbook_reference}: extracted {len(chunks)} chunks")
                    
                    document_result = supabase.table("kb_documents").insert({
                        "client_id": client_id,
                        "doc_type": "runbook",
                        "source_ref": runbook_reference,
                        "title": runbook_data.get("title"),
                        "content_hash": content_hash,
                        "metadata": runbook_metadata
                    }).execute()
                    
                    document_uuid = document_result.data[0]["id"]
                    logger.debug(f"Created document record with UUID: {document_uuid}")
                    
                    if chunks:
                        chunk_texts = [chunk["text"] for chunk in chunks]
                        embeddings = generate_embeddings_batch(chunk_texts)
                        
                        chunk_records = []
                        for i, chunk in enumerate(chunks):
                            chunk_records.append({
                                "document_id": document_uuid,
                                "client_id": client_id,
                                "doc_type": "runbook",
                                "chunk_index": chunk["metadata"]["chunk_index"],
                                "chunk_text": chunk["text"],
                                "metadata": chunk["metadata"],
                                "embedding": embeddings[i]
                            })
                            
                            logger.debug(f"Chunk {chunk['metadata']['chunk_index']}: section={chunk['metadata'].get('section', 'N/A')}, "
                                        f"subsection={chunk['metadata'].get('subsection', 'N/A')}, "
                                        f"length={len(chunk['text'])} chars")
                        
                        supabase.table("kb_embeddings").insert(chunk_records).execute()
                        logger.info(f"Inserted {len(chunk_records)} chunks into kb_embeddings")
                        total_chunks += len(chunk_records)
                
                except Exception as e:
                    logger.error(f"Error processing runbook {runbook_reference}: {str(e)}")
                    skipped_runbooks += 1
                    continue
        
        logger.info(f"Runbook ingestion completed. Total chunks inserted: {total_chunks}, Runbooks skipped: {skipped_runbooks}")
        
    except Exception as e:
        logger.error(f"Error during runbook ingestion: {str(e)}")
        raise


def structure_runbook_text(runbook_data: dict) -> str:
    text_parts = []
    
    # Header section
    text_parts.append(f"# {runbook_data.get('title', 'Unknown Runbook')}")
    text_parts.append(f"Runbook ID: {runbook_data.get('runbook_id', 'N/A')}")
    text_parts.append(f"Client: {runbook_data.get('client', 'N/A')}")
    text_parts.append(f"Account ID: {runbook_data.get('account_id', 'N/A')}")
    text_parts.append(f"Severity: {runbook_data.get('severity', 'N/A')}")
    text_parts.append("")
    
    # Description
    if runbook_data.get('description'):
        text_parts.append("## Description")
        text_parts.append(runbook_data['description'])
        text_parts.append("")
    
    # Affected Systems
    if runbook_data.get('affected_systems'):
        text_parts.append("## Affected Systems")
        for system in runbook_data['affected_systems']:
            text_parts.append(f"• {system}")
        text_parts.append("")
    
    # Services
    if runbook_data.get('services'):
        text_parts.append("## Services")
        for service in runbook_data['services']:
            text_parts.append(f"• {service}")
        text_parts.append("")
    
    # Triggers
    if runbook_data.get('triggers'):
        text_parts.append("## Triggers")
        for trigger in runbook_data['triggers']:
            text_parts.append(f"• {trigger}")
        text_parts.append("")
    
    # Immediate Actions
    if runbook_data.get('immediate_actions'):
        text_parts.append("## Immediate Actions")
        for i, action in enumerate(runbook_data['immediate_actions'], 1):
            text_parts.append(f"{i}. {action}")
        text_parts.append("")
    
    # Investigation Steps
    if runbook_data.get('investigation_steps'):
        text_parts.append("## Investigation Steps")
        for i, step in enumerate(runbook_data['investigation_steps'], 1):
            text_parts.append(f"{i}. {step}")
        text_parts.append("")
    
    # Resolution Steps
    if runbook_data.get('resolution_steps'):
        text_parts.append("## Resolution Steps")
        for i, step in enumerate(runbook_data['resolution_steps'], 1):
            text_parts.append(f"{i}. {step}")
        text_parts.append("")
    
    # Verification
    if runbook_data.get('verification'):
        text_parts.append("## Verification")
        for i, step in enumerate(runbook_data['verification'], 1):
            text_parts.append(f"{i}. {step}")
        text_parts.append("")
    
    # Escalation Contacts
    if runbook_data.get('escalation_contacts'):
        text_parts.append("## Escalation Contacts")
        for contact in runbook_data['escalation_contacts']:
            text_parts.append(f"• {contact}")
        text_parts.append("")
    
    # Special Considerations
    if runbook_data.get('special_considerations'):
        text_parts.append("## Special Considerations")
        for consideration in runbook_data['special_considerations']:
            text_parts.append(f"• {consideration}")
        text_parts.append("")
    
    # Additional metadata
    if runbook_data.get('estimated_resolution_time'):
        text_parts.append("## Estimated Resolution Time")
        text_parts.append(runbook_data['estimated_resolution_time'])
        text_parts.append("")
    
    if runbook_data.get('last_updated'):
        text_parts.append("## Last Updated")
        text_parts.append(runbook_data['last_updated'])
        text_parts.append("")
    
    return "\n".join(text_parts)


def main():
    logger.info("Starting ingestion pipeline...")
    
    # Validate environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    drive_cod_folder_id = os.environ.get("DRIVE_COD_FOLDER_ID")
    wiki_url = os.environ.get("WIKI_URL")
    
    if not supabase_url:
        raise ValueError("SUPABASE_URL is not set")   
    
    if not supabase_service_key:
        raise ValueError("SUPABASE_SERVICE_KEY is not set")   
    
    if not drive_cod_folder_id:
        raise ValueError("DRIVE_COD_FOLDER_ID is not set")   
    
    if not wiki_url:
        logger.warning("WIKI_URL is not set. Runbook ingestion will be skipped.")
    
    logger.info("Environment variables validated successfully")
    
    # Initialize Supabase client
    supabase = create_client(
        supabase_url,
        supabase_service_key
    )
    logger.info("Supabase client initialized")
    
    # Ingest CoD documents
    ingest_cod_documents(supabase, drive_cod_folder_id)
    
    # Ingest runbooks
    ingest_runbooks(supabase)
    
    logger.info("Ingestion pipeline completed successfully")


if __name__ == '__main__':
    main()