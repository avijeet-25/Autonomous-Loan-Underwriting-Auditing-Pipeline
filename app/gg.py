from typing import TypedDict, Annotated, Sequence, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# 1. Define the Centralized System State
class AgentState(TypedDict):
    """
    The unified state object passed between all nodes in our LangGraph pipeline.
    Uses Annotated[..., add] to continuously append incoming messages and logs
    without overwriting historical execution traces.
    """
    # Raw verified inputs passed from the FastAPI schema
    client_profile: Dict[str, Any]
    
    # Message tracking for the LLM ReAct conversation loop
    messages: Annotated[Sequence[BaseMessage], add]
    
    # Internal runtime execution state variables
    current_node: str
    underwriting_metrics: Dict[str, Any]
    blacklist_status: str
    vintage_status: str
    final_verdict: str  # "APPROVED", "REJECTED", or "MANUAL_REVIEW"
    
    # Real-time tracking log list that our Streamlit UI reads line-by-line
    execution_logs: Annotated[list[str], add]


# 2. Define Node Skeletons (We will bind our agents to these in the next file)
async def data_ingestion_node(state: AgentState) -> Dict[str, Any]:
    """Parses initial Pydantic payload and sets up systemic flags."""
    return {
        "current_node": "DATA_INGESTION",
        "execution_logs": ["Data Ingestion Node: Initialized financial state markers successfully."]
    }

async def financial_analyst_node(state: AgentState) -> Dict[str, Any]:
    """Runs calculation loops and analyzes risk ratios."""
    return {
        "current_node": "FINANCIAL_ANALYST_AGENT",
        "execution_logs": ["Financial Analyst Node: Booting ReAct model to process credit and ratio metrics."]
    }

async def compliance_auditor_node(state: AgentState) -> Dict[str, Any]:
    """Executes RAG lookups against internal compliance documents."""
    return {
        "current_node": "COMPLIANCE_AUDITOR_AGENT",
        "execution_logs": ["Compliance Auditor Node: Querying policy vectors and preparing reranker filtering."]
    }

async def final_execution_node(state: AgentState) -> Dict[str, Any]:
    """Finalizes application state records and saves decision outcomes."""
    return {
        "current_node": "EXECUTION_NODE",
        "execution_logs": ["Final Execution Node: Persisting underwriting verdict and broadcasting alerts."]
    }


# 3. Define Conditional Routing Logic (The Graph Edges)
def router_edge(state: AgentState) -> str:
    """
    Acts as a traffic cop. Examines the state variables dynamically 
    to decide the next execution path or terminate early if high risks are found.
    """
    # If the financial checks or database blacklists show a direct failure, 
    # we can bypass the rest of the pipeline and route straight to final execution.
    if state.get("blacklist_status") == "FLAGGED":
        return "route_to_execution"
    
    # Default sequential operational path
    current = state.get("current_node")
    if current == "DATA_INGESTION":
        return "route_to_analyst"
    elif current == "FINANCIAL_ANALYST_AGENT":
        return "route_to_auditor"
    
    return "route_to_execution"


# 4. Construct and Compile the State Graph Network
workflow = StateGraph(AgentState)

# Add our active processing components (Nodes)
workflow.add_node("ingestion", data_ingestion_node)
workflow.add_node("analyst", financial_analyst_node)
workflow.add_node("auditor", compliance_auditor_node)
workflow.add_node("execution", final_execution_node)

# Establish Entry Point
workflow.set_entry_point("ingestion")

# Configure Conditional and Direct Routing (Edges)
workflow.add_conditional_edges(
    "ingestion",
    router_edge,
    {
        "route_to_analyst": "analyst",
        "route_to_execution": "execution"
    }
)

workflow.add_conditional_edges(
    "analyst",
    router_edge,
    {
        "route_to_auditor": "auditor",
        "route_to_execution": "execution"
    }
)

# Connect remaining paths directly to the finish line
workflow.add_edge("auditor", "execution")
workflow.add_edge("execution", END)

# Compile the execution graph blueprint
compiled_graph = workflow.compile()





















































