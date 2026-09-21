import re
from typing import List, Dict

# Pattern to match section headers in plain text
# Section headers are typically standalone lines that start with capital letters
# and are followed by content or bullet points
SECTION_PATTERN = re.compile(r'^([A-Z][A-Za-z\s]+)$', re.MULTILINE)

# Pattern to match subsection headers (like application names within Applications section)
SUBSECTION_PATTERN = re.compile(r'^([A-Z][A-Za-z\s]+Pro|^[A-Z][A-Za-z\s]+Online|^[A-Z][A-Za-z\s]+Hub|^[A-Z][A-Za-z\s]+Mobile|^[A-Z][A-Za-z\s]+API|^[A-Z][A-Za-z\s]+Gateway|^[A-Z][A-Za-z\s]+Plus)$', re.MULTILINE)

# Maximum chunk size for very long sections
MAX_SECTION_SIZE = 1000


def chunk_by_sections(text: str, metadata: Dict = None) -> List[Dict]:
    """
    Split text into chunks based on section headers in plain text format.
    
    Args:
        text (str): The document text to chunk
        metadata (Dict): Base metadata to include in each chunk
        
    Returns:
        List[Dict]: List of chunk records with keys:
            - text: chunk content
            - metadata: chunk-specific metadata including section info
            - chunk_index: sequential index
    """
    if metadata is None:
        metadata = {}
    
    chunks = []
    
    # Known section headers from the CoD format
    known_sections = {
        "Client Details", "IT Environment", "Applications", "Infrastructure",
        "Architecture & Dependencies", "Monitoring & Observability", "Escalations",
        "Special Instructions", "Monitoring Services", "Key Alerts", "Log Management",
        "Primary Contacts", "Escalation Matrix", "Communication Channels"
    }
    
    # Split by lines to detect section headers
    lines = text.split('\n')
    
    current_section = "Document Header"
    current_chunk = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            # Preserve paragraph breaks
            if current_chunk:
                current_chunk += "\n"
            continue
        
        # Check if this line is a section header
        is_section_header = (
            line in known_sections or
            (len(line.split()) <= 4 and 
             line[0].isupper() and 
             not line.endswith('.') and
             ':' not in line and
             not line.startswith('•'))
        )
        
        if is_section_header:
            # Save current chunk if it exists
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": {
                        **metadata,
                        "section": current_section,
                        "chunk_index": len(chunks)
                    }
                })
                current_chunk = ""
            
            current_section = line
            # Don't include the header line in the chunk content
            continue
        
        # Add line to current chunk
        if current_chunk:
            current_chunk += "\n" + line
        else:
            current_chunk = line
        
        # Check if chunk is too large
        if len(current_chunk) > MAX_SECTION_SIZE:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    **metadata,
                    "section": current_section,
                    "chunk_index": len(chunks)
                }
            })
            current_chunk = ""
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {
                **metadata,
                "section": current_section,
                "chunk_index": len(chunks)
            }
        })
    
    # If no chunks were created, treat entire document as one chunk
    if not chunks:
        chunks.append({
            "text": text,
            "metadata": {
                **metadata,
                "section": "Document",
                "chunk_index": 0
            }
        })
    
    return chunks


def extract_section_metadata(text: str) -> Dict:
    """
    Extract structured metadata from document text based on Client Details section.
    
    Args:
        text (str): The document text
        
    Returns:
        Dict: Extracted metadata (account_id, company_name, etc.)
    """
    metadata = {}
    
    # Look for Client Details section in plain text format
    lines = text.split('\n')
    
    in_client_details = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line == "Client Details":
            in_client_details = True
            continue
        
        if in_client_details:
            # Check if we've moved to a new section
            if line and line[0].isupper() and len(line.split()) <= 3 and ':' not in line:
                break
            
            # Extract key-value pairs from bullet points
            if line.startswith('•'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].replace('•', '').strip()
                    value = parts[1].strip()
                    
                    # Normalize key names
                    if 'Company Name' in key:
                        metadata["company_name"] = value
                    elif 'Account ID' in key:
                        metadata["account_id"] = value
                    elif 'Industry' in key:
                        metadata["industry"] = value
                    elif 'Primary Region' in key:
                        metadata["primary_region"] = value
                    elif 'Timezone' in key:
                        metadata["timezone"] = value
                    elif 'Business Unit' in key:
                        metadata["business_unit"] = value
    
    return metadata


if __name__ == "__main__":
    # Test the chunker with sample text that matches actual PDF output format
    sample_text = """Northstar Health Systems - Client
Operations Documentation

Client Details
• Company Name: Northstar Health Systems
• Account ID: ACC-1001
• Industry: Healthcare
• Company Size: Enterprise
• Primary Region: US
• Timezone: America/New_York
• Business Unit: Clinical Operations & IT Infrastructure

IT Environment
• Cloud Provider: AWS (us-east-1)
• On-Premises: Hybrid deployment with 3 data centers (New York, Boston, Philadelphia)
• Infrastructure Type: Healthcare-grade HIPAA-compliant infrastructure

Applications
MedChart Pro
• Description: Enterprise Electronic Health Records system managing patient medical records, treatment plans, and clinical documentation across 12 hospitals and 45 clinics
• Type: Clinical Application
• Criticality: Critical
• Technology Stack: Oracle Database, Java EE, HL7 FHIR API

CareConnect API
• Description: Clinical API platform enabling interoperability between EHR systems, lab systems, imaging systems, and third-party healthcare applications
• Type: Integration Platform
• Criticality: Critical
• Technology Stack: Node.js, PostgreSQL, REST/GraphQL APIs

Infrastructure
Load Balancers
• Primary: AWS Application Load Balancers (ALB) for web tier
• Secondary: F5 Big-IP for clinical application traffic
• Configuration: Health-based routing with SSL termination

Identity & Access Management
• Provider: Microsoft Azure Active Directory
• MFA: Duo Security for clinical staff access
• Role-Based Access: Granular permissions by clinical role and department"""
    
    chunks = chunk_by_sections(sample_text)
    print(f"Generated {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"Section: {chunk['metadata'].get('section', 'N/A')}")
        print(f"Text preview: {chunk['text'][:150]}...")
        print(f"Length: {len(chunk['text'])} chars")
    
    # Test metadata extraction
    print("\n\nExtracted metadata:")
    metadata = extract_section_metadata(sample_text)
    for key, value in metadata.items():
        print(f"{key}: {value}")