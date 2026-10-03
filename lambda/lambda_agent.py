import os
import requests
import json
import sys
import uuid
import logging
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("lambda_agent")

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from retrieval import retrieve_knowledge_chunks
from shared.models import QueryRequest

class LambdaAgent:    
    def __init__(self, system_prompt_path: str = "system_prompt.txt"):
        load_dotenv()
        logger.info("Initializing LambdaAgent")
        
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        self.model = init_chat_model(
            "openai/gpt-oss-20b",
            model_provider="groq",
            temperature=0,
        )
        
        self.system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
        
        self.checkpointer = InMemorySaver()
        
        # Define tools as standalone functions to avoid self parameter issues
        def get_slas_by_client(client_id: str, priority: str = None):
            """Retrieve SLA requirements and priority-specific response targets for a client.

            Example usage:
                get_slas_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651", priority="P1")
            """
            logger.info("Tool call: get_slas_by_client | client_id=%s priority=%s", client_id, priority)
            try:
                api_url = f"http://localhost:5001/api/slas/client/{client_id}"
                params = {}
                if priority:
                    params["priority"] = priority
                response = requests.get(api_url, params=params, timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_slas_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_slas_by_client | client_id=%s", client_id)
                return f"Error fetching SLA data: {str(e)}"

        def get_special_instructions_by_client(client_id: str):
            """Retrieve client special handling instructions, escalation notes, or operational constraints.
Returns special instruction data with resource type "special_instruction" containing id and instruction fields.

            Example usage:
                get_special_instructions_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651")
            """
            logger.info("Tool call: get_special_instructions_by_client | client_id=%s", client_id)
            try:
                response = requests.get(f"http://localhost:5001/api/special_instructions/client/{client_id}", timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_special_instructions_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_special_instructions_by_client | client_id=%s", client_id)
                return f"Error fetching special instructions: {str(e)}"

        def get_contacts_by_client(client_id: str):
            """Retrieve contact records for a client, including primary support contacts and escalation channels.
Returns contact data with resource type "contact" containing id, service_manager, and other contact fields.

            Example usage:
                get_contacts_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651")
            """
            logger.info("Tool call: get_contacts_by_client | client_id=%s", client_id)
            try:
                response = requests.get(f"http://localhost:5001/api/contacts/client/{client_id}", timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_contacts_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_contacts_by_client | client_id=%s", client_id)
                return f"Error fetching contacts: {str(e)}"

        def get_services_by_client(client_id: str):
            """Retrieve services and supported environment details configured for the client.
Returns service data with resource type "service" containing id and service_name fields.

            Example usage:
                get_services_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651")
            """
            logger.info("Tool call: get_services_by_client | client_id=%s", client_id)
            try:
                response = requests.get(f"http://localhost:5001/api/services/client/{client_id}", timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_services_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_services_by_client | client_id=%s", client_id)
                return f"Error fetching services: {str(e)}"

        def get_critical_systems_by_client(client_id: str):
            """Retrieve critical systems or business dependencies for a client.
Returns critical system data with resource type "critical_system" containing id and system_name fields.

            Example usage:
                get_critical_systems_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651")
            """
            logger.info("Tool call: get_critical_systems_by_client | client_id=%s", client_id)
            try:
                response = requests.get(f"http://localhost:5001/api/critical_systems/client/{client_id}", timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_critical_systems_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_critical_systems_by_client | client_id=%s", client_id)
                return f"Error fetching critical systems: {str(e)}"

        def get_runbooks_by_client(client_id: str):
            """Retrieve client-specific runbook references and metadata.
Returns runbook data with resource type "runbook" containing id and runbook_reference fields.

            Example usage:
                get_runbooks_by_client(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651")
            """
            logger.info("Tool call: get_runbooks_by_client | client_id=%s", client_id)
            try:
                response = requests.get(f"http://localhost:5001/api/runbooks/client/{client_id}", timeout=20)
                response.raise_for_status()
                payload = response.json()
                logger.info(
                    "Tool result: get_runbooks_by_client | client_id=%s status=%s count=%s",
                    client_id,
                    response.status_code,
                    len(payload) if isinstance(payload, list) else "n/a",
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_runbooks_by_client | client_id=%s", client_id)
                return f"Error fetching runbooks: {str(e)}"

        def get_cod_documents(client_id: str, query_context: str):
            """Retrieve relevant COD (Client-onboarding documents) knowledge chunks for a client.

            This tool searches the knowledge base for COD documents only, which contain
            operational procedures, standard operating procedures, and institutional knowledge.
            Returns COD document data with resource type "cod" containing document_id (for Google Drive URL) and title fields.

            Example usage:
                get_cod_documents(
                    client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651",
                    query_context="P1 outage on StayEase PMS with database timeouts after RDS maintenance"
                )
            """
            logger.info(
                "Tool call: get_cod_documents | client_id=%s query_context_length=%s",
                client_id,
                len(query_context or ""),
            )
            try:
                chunks = retrieve_knowledge_chunks(
                    query=query_context,
                    client_id=client_id,
                    doc_types=["cod"],
                    match_threshold=0.5,
                    match_count=5
                )
                
                if not chunks:
                    logger.info("Tool result: get_cod_documents | client_id=%s matches=0", client_id)
                    return "No relevant information found for this query context."

                formatted_results = []
                for chunk in chunks:
                    metadata = chunk.get("metadata") or {}

                    formatted_results.append({
                        "id": str(chunk.get("document_id")),
                        "title": chunk.get("title", "Untitled document"),
                        "type": chunk.get("doc_type", "unknown"),
                        "similarity": chunk.get("similarity", 0),
                        "content": chunk.get("chunk_text", ""),
                        "metadata": metadata
                    })

                logger.info(
                    "Tool result: get_cod_documents | client_id=%s matches=%s",
                    client_id,
                    len(formatted_results),
                )
                return formatted_results
            except Exception as e:
                logger.exception("Tool error: get_cod_documents | client_id=%s", client_id)
                return f"Error retrieving information: {str(e)}"
        
        # Create tools with the decorator
        self.get_slas_tool = tool(get_slas_by_client)
        self.get_special_instructions_tool = tool(get_special_instructions_by_client)
        self.get_contacts_tool = tool(get_contacts_by_client)
        self.get_services_tool = tool(get_services_by_client)
        self.get_critical_systems_tool = tool(get_critical_systems_by_client)
        self.get_runbooks_by_client_tool = tool(get_runbooks_by_client)
        self.get_cod_documents_tool = tool(get_cod_documents)
        
        self.agent = create_agent(
            model=self.model,
            tools=[
                self.get_slas_tool,
                self.get_special_instructions_tool,
                self.get_contacts_tool,
                self.get_services_tool,
                self.get_critical_systems_tool,
                self.get_runbooks_by_client_tool,
                self.get_cod_documents_tool,
            ],
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
        )

    
    def process_query(self, request: QueryRequest, thread_id: str = None) -> tuple:
        user_content = request.query
        logger.info(
            "Processing query | client_id=%s thread_id=%s query_prefix=%s",
            request.client_id,
            thread_id,
            request.query[:80],
        )

        context_info = []

        if request.client_id:
            context_info.append(f"Client ID: {request.client_id}")

        if request.metadata:
            context_info.append(f"Metadata: {request.metadata}")
    
        if context_info:
            user_content = (
                f"{request.query}\n\n"
                f"[Context: {', '.join(context_info)}]"
            )
    
        if thread_id is None:
            thread_id = str(uuid.uuid4())
            logger.info("Created new thread_id=%s", thread_id)
    
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
    
        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ]
            },
            config=config,
        )
    
        last_message = result["messages"][-1]
        content = last_message.content

        logger.info("Raw content type: %s", type(content))
        logger.info("Raw content length: %s", len(str(content)) if content else 0)

        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and "text" in content[0]:
                content = content[0]["text"]
            else:
                content = str(content[0])

        if not isinstance(content, str):
            content = str(content)

        logger.info("Content before JSON parse: %s", content[:500] if len(content) > 500 else content)

        try:
            response = json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception("Agent returned invalid JSON for thread_id=%s", thread_id)
            logger.error("Full content that failed to parse: %s", content)
            raise ValueError(
                f"Agent returned invalid JSON: {e}\n"
                f"Raw response: {content}"
            )
    
        # Validate the expected structure
        if not isinstance(response, dict):
            logger.error("Agent response is not a JSON object for thread_id=%s | type=%s", thread_id, type(response).__name__)
            raise ValueError(
                f"Agent response must be a JSON object, got: {type(response).__name__}"
            )
    
        response.setdefault("message", "")
        response.setdefault("resources", [])
        logger.info("Completed query for thread_id=%s | response_fields=%s", thread_id, sorted(response.keys()))
        return response, thread_id


if __name__ == "__main__":
    agent = LambdaAgent()
    
    simple_query = """HarborView Hotels P1 Incident - StayEase PMS Connectivity Issues

Environment Details:
- Client: HarborView Hotels (ACC-1009)
- Client ID: dd23437f-7ea7-4c46-8beb-4e2b4e555651
- Affected System: StayEase PMS
- Impact: 8 out of 12 hotel properties unable to process check-ins/check-outs
- Time: Peak check-in period (2:00 PM - 4:00 PM Singapore time)
- Error Pattern: Intermittent database connection timeouts to SQL Server
- Recent Changes: AWS RDS maintenance window completed 2 hours ago
- Business Impact: Guests waiting in lobby, revenue loss from delayed check-ins

Load the context for this incident. Review the client context and applicable SLA/priority requirements, and summarize the key information I should know before investigating the incident. Do not troubleshoot yet or make assumptions beyond the retrieved information.
"""
    
    query_request = QueryRequest(
        query=simple_query,
        client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651",
        metadata={"severity": "P1", "affected_system": "StayEase PMS"}
    )
    
    guidance, thread_id = agent.process_query(query_request)
    
    logger.info("=%s", "=" * 80)
    logger.info("INCIDENT GUIDANCE DOCUMENT")
    logger.info("Thread ID: %s", thread_id)
    logger.info("=%s", "=" * 80)
    logger.info("%s", guidance)
    logger.info("=%s", "=" * 80)
    
    follow_up_request = QueryRequest(
        query="What are the specific steps to flush the connection pools?",
        client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651"
    )
    
    follow_up_guidance, same_thread_id = agent.process_query(follow_up_request, thread_id)
    
    logger.info("\n%s", "=" * 80)
    logger.info("FOLLOW-UP RESPONSE")
    logger.info("Thread ID: %s", same_thread_id)
    logger.info("=%s", "=" * 80)
    logger.info("%s", follow_up_guidance)
    logger.info("=%s", "=" * 80)