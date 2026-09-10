import os
import json
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)

BUCKET_NAME = 'runbooks'
RUNBOOKS_DIR = Path(__file__).parent / 'runbooks'

def upload_runbooks():
    
    if not RUNBOOKS_DIR.exists():
        print(f"Error: Runbooks directory not found at {RUNBOOKS_DIR}")
        return
    
    runbook_files = list(RUNBOOKS_DIR.glob("*.json"))
    
    if not runbook_files:
        print(f"No JSON files found in {RUNBOOKS_DIR}")
        return
    
    print(f"Found {len(runbook_files)} runbook files to upload")
    
    # Try to create bucket (may fail if already exists)
    try:
        supabase.storage.create_bucket(
            BUCKET_NAME,
            options={"public": False}
        )
        print(f"Created bucket: {BUCKET_NAME}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Bucket {BUCKET_NAME} already exists")
        else:
            print(f"Error creating bucket: {e}")
            return
    
    success_count = 0
    error_count = 0
    
    for runbook_file in runbook_files:
        try:
            with open(runbook_file, 'r') as f:
                runbook_data = json.load(f)
            
            runbook_json = json.dumps(runbook_data, indent=2)
            
            file_path = runbook_file.name
            supabase.storage.from_(BUCKET_NAME).upload(
                path=file_path,
                file=runbook_json.encode('utf-8'),
                file_options={"content-type": "application/json"}
            )
            
            print(f"Uploaded: {file_path}")
            success_count += 1
            
        except Exception as e:
            print(f"Failed to upload {runbook_file.name}: {e}")
            error_count += 1
    
    print(f"\nUpload complete: {success_count} successful, {error_count} failed")

if __name__ == "__main__":
    upload_runbooks()



