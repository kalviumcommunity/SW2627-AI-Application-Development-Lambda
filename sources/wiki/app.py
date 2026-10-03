import os
import json

from flask import Flask, render_template
from dotenv import load_dotenv
from supabase import create_client, Client
from flask_cors import CORS


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
CORS(app)

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


@app.route("/sla/<sla_id>")
def sla(sla_id):
    response = supabase.table("slas") \
        .select("""
            *,
            sla_priorities (*)
        """) \
        .eq("id", sla_id) \
        .execute()

    if not response.data:
        return "SLA not found", 404
    sla_data = response.data[0]
    return render_template(
        "sla.html",
        sla=sla_data
    )


@app.route("/service/<service_id>")
def service(service_id):
    response = supabase.table("services") \
        .select("*") \
        .eq("id", service_id) \
        .execute()

    if not response.data:
        return "Service not found", 404

    service_data = response.data[0]
    return render_template(
        "service.html",
        service=service_data
    )


@app.route("/critical-system/<system_id>")
def critical_system(system_id):
    response = supabase.table("critical_systems") \
        .select("*") \
        .eq("id", system_id) \
        .execute()

    if not response.data:
        return "Critical system not found", 404

    system_data = response.data[0]
    return render_template(
        "critical_system.html",
        system=system_data
    )


@app.route("/contact/<contact_id>")
def contact(contact_id):
    response = supabase.table("contacts") \
        .select("*") \
        .eq("id", contact_id) \
        .execute()

    if not response.data:
        return "Contact not found", 404

    contact_data = response.data[0]
    return render_template(
        "contact.html",
        contact=contact_data
    )


@app.route("/special-instruction/<instruction_id>")
def special_instruction(instruction_id):
    response = supabase.table("special_instructions") \
        .select("*") \
        .eq("id", instruction_id) \
        .execute()

    if not response.data:
        return "Special instruction not found", 404

    instruction_data = response.data[0]
    return render_template(
        "special_instruction.html",
        instruction=instruction_data
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


from flask import request

@app.route("/api/slas/client/<client_id>")
def get_slas_by_client_id(client_id):
    priority = request.args.get("priority")
    
    query = supabase.table("slas") \
        .select("""
            *,
            sla_priorities (*)
        """) \
        .eq("client_id", client_id)
    
    response = query.execute()
    slas = response.data

    if priority:
        priority_clean = priority.strip().upper()
        # Filter priorities within each SLA, or filter SLAs that match priority
        filtered_slas = []
        for sla in slas:
            matching_priorities = [
                p for p in sla.get("sla_priorities", [])
                if p.get("priority_level", "").upper() == priority_clean
                   or priority_clean in p.get("priority_name", "").upper()
            ]
            if matching_priorities:
                sla_copy = dict(sla)
                sla_copy["sla_priorities"] = matching_priorities
                filtered_slas.append(sla_copy)
        return filtered_slas

    return slas


@app.route("/api/special_instructions/client/<client_id>")
def get_special_instructions_by_client_id(client_id):
    response = supabase.table("special_instructions") \
        .select("*") \
        .eq("client_id", client_id) \
        .execute()
    return response.data


@app.route("/api/contacts/client/<client_id>")
def get_contacts_by_client_id(client_id):
    response = supabase.table("contacts") \
        .select("*") \
        .eq("client_id", client_id) \
        .execute()
    return response.data


@app.route("/api/services/client/<client_id>")
def get_services_by_client_id(client_id):
    response = supabase.table("services") \
        .select("*") \
        .eq("client_id", client_id) \
        .execute()
    return response.data


@app.route("/api/critical_systems/client/<client_id>")
def get_critical_systems_by_client_id(client_id):
    response = supabase.table("critical_systems") \
        .select("*") \
        .eq("client_id", client_id) \
        .execute()
    return response.data


@app.route("/api/context/client/<client_id>")
def get_unified_client_context(client_id):
    priority = request.args.get("priority")
    slas = get_slas_by_client_id(client_id)
    instructions = supabase.table("special_instructions").select("*").eq("client_id", client_id).execute().data
    contacts = supabase.table("contacts").select("*").eq("client_id", client_id).execute().data
    services = supabase.table("services").select("*").eq("client_id", client_id).execute().data

    return {
        "client_id": client_id,
        "slas": slas,
        "special_instructions": instructions,
        "contacts": contacts,
        "services": services
    }



if __name__ == "__main__":
    app.run(port="5001")

