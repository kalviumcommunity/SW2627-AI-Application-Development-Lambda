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
    def __init__(self, system_prompt_path: str = "system_prompt.txt", max_history_messages: int = 10):
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
        self.max_history_messages = max_history_messages
        
        # Persistent context storage per thread
        self.thread_context = {}  # thread_id -> {"client_context": dict, "summary": str, "priority": str}
        
        # Define tools as standalone functions to avoid self parameter issues
        def get_client_context(client_id: str, priority: str = None, include_slas: bool = True, include_instructions: bool = True, include_contacts: bool = False, include_services: bool = True, include_critical_systems: bool = False, include_runbooks: bool = False):
            """Retrieve client context data selectively. Only fetch what you need to minimize token usage.

            Parameters:
            - client_id: Required client identifier
            - priority: Optional priority level for SLA filtering
            - include_slas: Include SLA data (default: True)
            - include_instructions: Include special instructions (default: True)
            - include_contacts: Include contact information (default: False)
            - include_services: Include service information (default: True)
            - include_critical_systems: Include critical systems (default: False)
            - include_runbooks: Include runbook references (default: False)

            Example usage:
                get_client_context(client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651", priority="P1", include_contacts=True)
            """
            logger.info("Tool call: get_client_context | client_id=%s priority=%s slas=%s instructions=%s contacts=%s services=%s critical_systems=%s runbooks=%s",
                        client_id, priority, include_slas, include_instructions, include_contacts, include_services, include_critical_systems, include_runbooks)
            try:
                payload = {"client_id": client_id}

                # Only fetch what's requested
                if include_slas or include_instructions or include_contacts or include_services:
                    api_url = f"http://localhost:5001/api/context/client/{client_id}"
                    params = {}
                    if priority:
                        params["priority"] = priority
                    response = requests.get(api_url, params=params, timeout=20)
                    response.raise_for_status()
                    context_data = response.json()

                    if include_slas:
                        payload["slas"] = context_data.get("slas", [])
                    if include_instructions:
                        payload["special_instructions"] = context_data.get("special_instructions", [])
                    if include_contacts:
                        payload["contacts"] = context_data.get("contacts", [])
                    if include_services:
                        payload["services"] = context_data.get("services", [])

                if include_critical_systems:
                    critical_systems = requests.get(f"http://localhost:5001/api/critical_systems/client/{client_id}", timeout=20).json()
                    payload["critical_systems"] = critical_systems

                if include_runbooks:
                    runbooks = requests.get(f"http://localhost:5001/api/runbooks/client/{client_id}", timeout=20).json()
                    payload["runbooks"] = runbooks

                logger.info(
                    "Tool result: get_client_context | client_id=%s slas=%s instructions=%s contacts=%s services=%s critical_systems=%s runbooks=%s",
                    client_id,
                    len(payload.get("slas", [])),
                    len(payload.get("special_instructions", [])),
                    len(payload.get("contacts", [])),
                    len(payload.get("services", [])),
                    len(payload.get("critical_systems", [])),
                    len(payload.get("runbooks", [])),
                )
                return payload
            except requests.exceptions.RequestException as e:
                logger.exception("Tool error: get_client_context | client_id=%s", client_id)
                return f"Error fetching client context: {str(e)}"

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
        self.get_client_context_tool = tool(get_client_context)
        self.get_cod_documents_tool = tool(get_cod_documents)

        self.agent = create_agent(
            model=self.model,
            tools=[
                self.get_client_context_tool,
                self.get_cod_documents_tool,
            ],
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
        )

    def _trim_conversation_history(self, thread_id: str):
        """Trim conversation history to keep only the last N messages to reduce token usage."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            current_state = self.checkpointer.get(config)

            if current_state and "channel_values" in current_state:
                messages = current_state["channel_values"].get("messages", [])

                if len(messages) > self.max_history_messages:
                    # Keep the most recent messages
                    trimmed_messages = messages[-self.max_history_messages:]
                    logger.info(
                        "Trimmed conversation history for thread_id=%s | from=%s to=%s messages",
                        thread_id,
                        len(messages),
                        len(trimmed_messages)
                    )

                    # Update the state with trimmed messages
                    current_state["channel_values"]["messages"] = trimmed_messages
                    self.checkpointer.put(config, current_state)
        except Exception as e:
            logger.warning("Failed to trim conversation history for thread_id=%s: %s", thread_id, e)

    def _update_context_summary(self, thread_id: str, new_info: str):
        """Update context summary with new relevant information."""
        if thread_id not in self.thread_context:
            self.thread_context[thread_id] = {"client_context": {}, "summary": "", "priority": None}
        
        current_summary = self.thread_context[thread_id]["summary"]
        if current_summary:
            updated_summary = f"{current_summary}\nKey finding: {new_info}"
        else:
            updated_summary = f"Key finding: {new_info}"
        
        self.thread_context[thread_id]["summary"] = updated_summary
        logger.info("Updated context summary for thread_id=%s | summary_length=%s", thread_id, len(updated_summary))

    def _get_context_for_injection(self, thread_id: str) -> str:
        """Get the context summary for injection into queries."""
        if thread_id not in self.thread_context:
            return ""
        
        context_data = self.thread_context[thread_id]
        parts = []
        
        if context_data.get("summary"):
            parts.append(f"Previously loaded context: {context_data['summary']}")
        
        if context_data.get("priority"):
            parts.append(f"Incident priority: {context_data['priority']}")
        
        return "\n".join(parts) if parts else ""

    
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
            # Extract priority from metadata for adaptive retrieval
            priority = request.metadata.get("priority") if request.metadata else None
            if priority and thread_id in self.thread_context:
                self.thread_context[thread_id]["priority"] = priority

        if context_info:
            user_content = (
                f"{request.query}\n\n"
                f"[Context: {', '.join(context_info)}]"
            )

        if thread_id is None:
            thread_id = str(uuid.uuid4())
            logger.info("Created new thread_id=%s", thread_id)
            # Initialize thread context
            self.thread_context[thread_id] = {"client_context": {}, "summary": "", "priority": request.metadata.get("priority") if request.metadata else None}
        else:
            # Trim conversation history for existing threads to reduce token usage
            self._trim_conversation_history(thread_id)
            # Inject stored context summary
            stored_context = self._get_context_for_injection(thread_id)
            if stored_context:
                user_content = f"{user_content}\n\n[Stored Context: {stored_context}]"

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
        
        # Detect initial context loading and store it
        if "Incident context loaded" in response.get("message", ""):
            logger.info("Detected initial context loading for thread_id=%s, storing context", thread_id)
            self.thread_context[thread_id]["client_context"] = {
                "resources": response.get("resources", []),
                "summary": response.get("message", "")
            }
            self.thread_context[thread_id]["summary"] = response.get("message", "")
        
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