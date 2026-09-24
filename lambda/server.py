from fastapi import FastAPI, HTTPException
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path to import shared models and lambda_agent
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from lambda_agent import LambdaAgent
from shared.models import QueryRequest, QueryResponse

app = FastAPI(title="Lambda Agent API", version="1.0.0")

agent = LambdaAgent()

@app.get("/")
async def root():
    return {"message": "Lambda Agent API is running", "status": "active"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_loaded": agent is not None}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, thread_id: str = None):
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process the query using the agent
        response, returned_thread_id = agent.process_query(request, thread_id)
        
        return QueryResponse(
            response=response, 
            success=True,
            thread_id=returned_thread_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)