import os
import requests
import warnings
import sys
import uuid
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from retrieval import retrieve_knowledge_chunks
from shared.models import QueryRequest

class LambdaAgent:    
    def __init__(self, system_prompt_path: str = "system_prompt.txt"):
        load_dotenv()
        
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        self.model = init_chat_model(
            "gemini-3.6-flash",
            model_provider="google_genai",
            temperature=0,
        )
        
        self.system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
        
        self.checkpointer = InMemorySaver()
        
        # Define tools as standalone functions to avoid self parameter issues
        def get_slas(client_id: str):
            """Retrieve SLA information for a specific client from the API."""
            try:
                api_url = f"http://localhost:5001/api/slas/client/{client_id}"
                response = requests.get(api_url)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                return f"Error fetching SLAs: {str(e)}"
        
        def get_runbooks_and_client_specific_info(client_id: str, query_context: str):
            """Retrieve relevant knowledge chunks and client-specific information."""
            try:
                chunks = retrieve_knowledge_chunks(
                    query=query_context,
                    client_id=client_id,
                    doc_types=["cod", "runbook"],
                    match_threshold=0.5,
                    match_count=5
                )
                
                if not chunks:
                    return "No relevant information found for this query context."
                
                formatted_results = []
                for chunk in chunks:
                    formatted_results.append({
                        "similarity": chunk.get('similarity', 0),
                        "document_type": chunk.get('doc_type', 'unknown'),
                        "content": chunk.get('chunk_text', ''),
                        "metadata": chunk.get('metadata', {})
                    })
                
                return formatted_results
            except Exception as e:
                return f"Error retrieving information: {str(e)}"
        
        # Create tools with the decorator
        self.get_slas_tool = tool(get_slas)
        self.get_runbooks_tool = tool(get_runbooks_and_client_specific_info)
        
        self.agent = create_agent(
            model=self.model,
            tools=[self.get_slas_tool, self.get_runbooks_tool],
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
        )
    
    def process_query(self, request: QueryRequest, thread_id: str = None) -> tuple:
        user_content = request.query
        
        # Add client ID and metadata to the message if provided
        context_info = []
        if request.client_id:
            context_info.append(f"Client ID: {request.client_id}")
        if request.metadata:
            context_info.append(f"Metadata: {request.metadata}")
        
        if context_info:
            user_content = f"{request.query}\n\n[Context: {', '.join(context_info)}]"
        
        # Create new thread_id if not provided
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        result = self.agent.invoke({
            "messages": [
                {"role": "user", "content": user_content}
            ]
        }, config=config)
        
        # Extract the actual text content from the response
        last_message = result["messages"][-1]
        content = last_message.content
        
        # Handle different response formats
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and "text" in content[0]:
                text_content = content[0]["text"]
            else:
                text_content = str(content[0])
        else:
            text_content = str(content)
        
        return text_content, thread_id


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

Please create a proper guidance document for the support engineer to get started with resolving this incident."""
    
    query_request = QueryRequest(
        query=simple_query,
        client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651",
        metadata={"severity": "P1", "affected_system": "StayEase PMS"}
    )
    
    # First query - creates new thread
    guidance, thread_id = agent.process_query(query_request)
    
    print("=" * 80)
    print("INCIDENT GUIDANCE DOCUMENT")
    print(f"Thread ID: {thread_id}")
    print("=" * 80)
    print(guidance)
    print("=" * 80)
    
    # Follow-up query using the same thread_id
    follow_up_request = QueryRequest(
        query="What are the specific steps to flush the connection pools?",
        client_id="dd23437f-7ea7-4c46-8beb-4e2b4e555651"
    )
    
    follow_up_guidance, same_thread_id = agent.process_query(follow_up_request, thread_id)
    
    print("\n" + "=" * 80)
    print("FOLLOW-UP RESPONSE")
    print(f"Thread ID: {same_thread_id}")
    print("=" * 80)
    print(follow_up_guidance)
    print("=" * 80)