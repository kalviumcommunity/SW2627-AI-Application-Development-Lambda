from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("server")

from lambda_agent import LambdaAgent
from lib.models import QueryRequest, QueryResponse

app = FastAPI(title="Lambda Agent API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("BEFORE: Starting LambdaAgent initialization")
# agent = LambdaAgent()
agent = None
logger.info("AFTER: LambdaAgent initialization completed")

@app.get("/")
async def root():
    return {"message": "Lambda Agent API is running", "status": "active"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_loaded": True}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, thread_id: str = None):
    try:
        if not request.query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty",
            )

        response, returned_thread_id = agent.process_query(
            request,
            thread_id,
        )

        return QueryResponse(
            message=response.get("message", ""),
            resources=response.get("resources", []),
            success=True,
            thread_id=returned_thread_id,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}",
        )

import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("LAMBDA_AGENT_PORT", "8000")))
    uvicorn.run(app, host=host, port=port)