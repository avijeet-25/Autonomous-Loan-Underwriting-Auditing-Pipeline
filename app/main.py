import os
import json
import asyncio
from fastapi import FASTAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import StreamingResponse

from app.schemas import LoanApplicationSchema
from app.graph import compiled_graph

app = FASTAPI(
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

    