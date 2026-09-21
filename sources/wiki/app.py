import os
import json

from flask import Flask, render_template
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


BUCKET_NAME = "runbooks"

app = Flask(__name__)

@app.route("/")
def index():
    response = supabase.table("runbook_references") \
        .select("""
            id,
            runbook_reference,
            created_at,
            client:clients (
                id,
                company_name
            )
        """).execute()
    grouped_runbooks = {}
    for runbook in response.data: 
        company_name = runbook["client"]["company_name"] 
        if company_name not in grouped_runbooks: 
            grouped_runbooks[company_name] = [] 
        grouped_runbooks[company_name].append(runbook) 
    return render_template( 
        "index.html", 
        grouped_runbooks=grouped_runbooks 
        )


@app.route("/runbook/<runbook_reference>")
def runbook(runbook_reference):
    file_content = supabase.storage \
        .from_(BUCKET_NAME) \
        .download(f"{runbook_reference}.json")
    runbook_data = json.loads(file_content)
    return render_template(
        "runbook.html",
        runbook=runbook_data
    )

@app.route("/api/runbook")
def get_runbooks_api():
    response = supabase.table("runbook_references") \
        .select("""
            id,
            runbook_reference,
            created_at,
            client:clients (
                id,
                company_name
            )
        """).execute()
    grouped_runbooks = {}
    for runbook in response.data: 
        company_name = runbook["client"]["company_name"] 
        if company_name not in grouped_runbooks: 
            grouped_runbooks[company_name] = [] 
        grouped_runbooks[company_name].append(runbook) 
    return grouped_runbooks


@app.route("/api/runbook/<runbook_reference>")
def get_runbook_reference_api(runbook_reference):
    file_content = supabase.storage \
        .from_(BUCKET_NAME) \
        .download(f"{runbook_reference}.json")
    runbook_data = json.loads(file_content)
    return runbook_data


@app.route("/api/runbooks/client/<client_id>")
def get_runbooks_by_client_id(client_id):
    response = supabase.table("runbook_references") \
        .select("""
            id,
            runbook_reference,
            created_at,
            client:clients (
                id,
                company_name
            )
        """) \
        .eq("client_id", client_id) \
        .execute()
    return response.data


@app.route("/api/slas/client/<client_id>")
def get_slas_by_client_id(client_id):
    response = supabase.table("slas") \
        .select("*") \
        .eq("client_id", client_id) \
        .execute()
    return response.data


if __name__ == "__main__":
    app.run(port="5001")
