import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyCoMqC2FknWg8wR_JGhpAyYq23c2Gf_tVY"
from dotenv import load_dotenv
load_dotenv() 
import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import StreamingResponse

from app.schemas import LoanApplicationSchema
from app.graph import compiled_graph

app = FastAPI(
    title="Aegis: Autonomous Underwriting Engine Core Server",
    description="Production-grade asynchronous multi-agent streaming API engine running LangGraph and Gemini 2.5 Flash",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def pipeline_stream_generator(validated_data: dict):
    """
    Asynchronous event generator that streams live execution updates from the
    LangGraph state ledger directly to the client as Server-Sent Events (SSE).
    """

    initial_state = {
        "client_profile": validated_data,
        "messages": [],
        "current_node": "START",
        "final_verdict": "PENDING",
        "execution_logs": ["System: Initializing multi-agent memory ledger frameworks..."]
    }

    try:
        async for chunk in compiled_graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_updates in chunk.items():

                current_node = state_updates.get("current_node", node_name).upper()
                new_logs = state_updates.get("execution_logs", [])

                for log in new_logs:
                    payload = {
                        "node": current_node,
                        "status": log
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                    await asyncio.sleep(0.04)

    except Exception as e:

        failure_payload = {
            "node": "CRITICAL_FAILURE",
            "status": f"Graph Runtime Aborted: {str(e)}"
        }
        yield f"data: {json.dumps(failure_payload)}\n\n"


@app.post("/api/v1/underwrite")
async def underwrite_loan_application_endpoint(application: LoanApplicationSchema):
    """
    Asynchronous REST API Gateway POST endpoint. Ingests raw client data payloads,
    forces pydantic v2 lifecycle checks, and instantiates the live graph event stream.
    """

    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="Infrastructure Deficit: GOOGLE_API_KEY environment variable is missing from the runtime host."
        )
    
    sanitized_profile = application.model_dump()

    return StreamingResponse(
        pipeline_stream_generator(sanitized_profile),
        media_type="text/event-stream"
    )

@app.get("/health")
def server_health_check():
    """Deterministic routing probe to verify active operational health state of the service instance."""
    return {"status": "healthy", "engine": "Aegis Core Machine", "version": "1.0.0"}


