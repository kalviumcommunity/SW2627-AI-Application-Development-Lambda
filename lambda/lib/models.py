# Shared models for query requests and responses

from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str
    client_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    message: str
    resources: list[dict[str, Any]] = []
    success: bool
    thread_id: str
