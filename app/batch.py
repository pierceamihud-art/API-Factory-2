"""Batch processing router for API Factory."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging
import time

from app.main import get_api_key
from app.model_adapter import ModelAdapter
from app.safety import content_validator
from app.metrics import REQUESTS_TOTAL, MODEL_ERRORS, SAFETY_BLOCKS

logger = logging.getLogger("api-factory")

router = APIRouter()

class BatchRequest(BaseModel):
    """Batch request with multiple inputs."""
    inputs: List[str] = Field(..., min_items=1, max_items=10)
    context: Optional[Dict] = None
    callback_url: Optional[str] = None

class BatchResponse(BaseModel):
    """Response for batch requests."""
    batch_id: str
    status: str
    results: Optional[List[Dict]] = None
    errors: Optional[List[str]] = None

# In-memory store for batch results (replace with Redis/DB in production)
_batch_store: Dict[str, Dict] = {}

async def process_batch(
    batch_id: str,
    inputs: List[str],
    context: Optional[Dict],
    model: ModelAdapter
):
    """Process a batch of inputs asynchronously."""
    results = []
    errors = []
    
    for input_text in inputs:
        try:
            # Validate content
            is_safe, issues = content_validator.validate(input_text)
            if not is_safe:
                for issue in issues:
                    SAFETY_BLOCKS.labels(rule_type=issue).inc()
                errors.append(f"Content validation failed for '{input_text[:20]}...': {issues}")
                continue

            # Generate response
            output = await model.generate(input_text, context)
            results.append({"input": input_text, "output": output})
            REQUESTS_TOTAL.labels(endpoint="/v1/batch", status="success").inc()
            
        except Exception as e:
            logger.error("Batch processing error: %s", str(e))
            MODEL_ERRORS.labels(model="batch", error_type="error").inc()
            errors.append(f"Processing failed for '{input_text[:20]}...': {str(e)}")

    _batch_store[batch_id].update({
        "status": "completed",
        "results": results,
        "errors": errors if errors else None,
        "completed_at": time.time()
    })

@router.post("/batch", response_model=BatchResponse)
async def create_batch(
    req: BatchRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Create and start a new batch processing job."""
    
    # Generate batch ID
    batch_id = f"batch_{int(time.time())}"
    
    # Store initial state
    _batch_store[batch_id] = {
        "status": "processing",
        "created_at": time.time(),
        "total_inputs": len(req.inputs)
    }
    
    # Start processing in background
    background_tasks.add_task(
        process_batch,
        batch_id,
        req.inputs,
        req.context,
        ModelAdapter()
    )
    
    return BatchResponse(
        batch_id=batch_id,
        status="processing"
    )

@router.get("/batch/{batch_id}", response_model=BatchResponse)
async def get_batch_status(
    batch_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get the status and results of a batch job."""
    
    batch = _batch_store.get(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
        
    return BatchResponse(
        batch_id=batch_id,
        status=batch["status"],
        results=batch.get("results"),
        errors=batch.get("errors")
    )