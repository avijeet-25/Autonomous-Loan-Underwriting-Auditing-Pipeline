import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Cleanly import our validation contract and compiled graph executor from package space
from app.schemas import LoanApplicationSchema
from app.graph import compiled_graph

# Initialize your core FastAPI enterprise web framework instance
app = FastAPI(
    title="Aegis: Autonomous Underwriting Engine Core Server",
    description="Production-grade asynchronous multi-agent streaming API engine running LangGraph and Gemini 2.5 Flash",
    version="1.0.0"
)

# Enforce strict Cross-Origin Resource Sharing (CORS) security guidelines
# This ensures external frontend frameworks (like Streamlit or React) can consume our endpoints safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In a locked-down production server, restrict this strictly to bank internal domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def pipeline_stream_generator(validated_data: dict):
    """
    Asynchronous event generator that streams live execution updates from the 
    LangGraph state ledger directly to the client as Server-Sent Events (SSE).
    """
    # Instantiate our baseline AgentState ledger map cleanly
    initial_state = {
        "client_profile": validated_data,
        "messages": [],
        "current_node": "START",
        "final_verdict": "PENDING",
        "execution_logs": ["System: Initializing multi-agent memory ledger frameworks..."]
    }

    try:
        # Run a native async iteration loop over our compiled graph updates stream
        # Using stream_mode="updates" yields the exact state delta the millisecond a node writes to the ledger
        async for chunk in compiled_graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_updates in chunk.items():
                
                # Gracefully intercept current active state parameters
                current_node = state_updates.get("current_node", node_name).upper()
                new_logs = state_updates.get("execution_logs", [])
                
                # Stream out each individual logged line in standard SSE compliant layout syntax
                for log in new_logs:
                    payload = {
                        "node": current_node,
                        "status": log
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    
                    # Add a micro-breathing delay to ensure smooth, human-scannable rendering animation on the frontend UI
                    await asyncio.sleep(0.04)
                    
    except Exception as e:
        # Strict defensive catch block to stream internal runtime failures directly down the connection pipe
        failure_payload = {
            "node": "CRITICAL_FAILURE",
            "status": f"Graph Runtime Aborted: {str(e)}"
        }
        yield f"data: {json.dumps(failure_payload)}\n\n"


@app.post("/api/v1/underwrite")
async def underwrite_loan_application_endpoint(application: LoanApplicationSchema):
    """
    Asynchronous REST API Gateway POST endpoint. Ingests raw client data payloads, 
    forces Pydantic v2 lifecycle checks, and instantiates the live graph event stream.
    """
    # Verify that your environment keys are loaded before initializing the graph run
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="Infrastructure Deficit: GOOGLE_API_KEY environment variable is missing from the runtime host."
        )
        
    # Safely dump our immutable Pydantic validation model out into a clean python dictionary matrix
    sanitized_profile = application.model_dump()
    
    # Return an HTTP 200 response streaming chunks back using a standard event-stream media descriptor
    return StreamingResponse(
        pipeline_stream_generator(sanitized_profile), 
        media_type="text/event-stream"
    )


@app.get("/health")
def server_health_check():
    """Deterministic routing probe to verify active operational health state of the service instance."""
    return {"status": "healthy", "engine": "Aegis Core Machine", "version": "1.0.0"}






































