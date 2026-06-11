from typing import TypedDict, Annotated, Sequence, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our custom package layers cleanly
from app.agents import data_ingestion_node, financial_analyst_agent, compliance_auditor_node
from app.tools import calculate_financial_ratios, check_internal_blacklist_registry, evaluate_vintage_eligibility

# ==========================================
# 🛡️ THE CENTRAL LEDGER (Agent State)
# ==========================================
class AgentState(TypedDict):
    client_profile: Dict[str, Any]                  # Read-only dictionary input of client attributes
    messages: Annotated[Sequence[BaseMessage], add]  # Appending message history ledger (The core shared memory)
    current_node: str                                # Pointer tracking which agent currently possesses execution control
    final_verdict: str                               # Terminal status across the framework ('PENDING', 'APPROVED', 'REJECTED')
    execution_logs: Annotated[list[str], add]        # Appending list of console string tracking steps for our UI


# ==========================================
# 🚦 THE COGNITIVE ROUTER EDGE
# ==========================================
def react_router_edge(state: AgentState) -> str:
    """
    True agentic edge router. Inspects the final entry of the central ledger's message history.
    If Gemini 2.5 Flash outputted a 'tool_calls' token signature, it routes execution to the tool node.
    If Gemini outputted a standard text response, it breaks the loop and transitions to the auditor.
    """
    messages_history = state["messages"]
    last_message = messages_history[-1]
    
    # Check if the model's response contains a structured function/tool call request
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    
    # If no tool signatures are requested, Gemini has concluded its analysis. Break the loop.
    return "end_loop"


# ==========================================
# 🏗️ COMPILING THE MULTI-AGENT STATE GRAPH
# ==========================================

# 1. Initialize a native LangGraph StateGraph pinned to our central ledger dictionary
workflow = StateGraph(AgentState)

# 2. Register our execution worker nodes into the graph workspace
workflow.add_node("ingestion", data_ingestion_node)
workflow.add_node("analyst_brain", financial_analyst_agent)
workflow.add_node("compliance_auditor", compliance_auditor_node)

# 3. Instantiate the native LangGraph ToolNode utility layer.
# This component automatically handles running the Python functions when requested by the model.
functional_tools_node = ToolNode([
    calculate_financial_ratios, 
    check_internal_blacklist_registry, 
    evaluate_vintage_eligibility
])
workflow.add_node("tools_runner", functional_tools_node)


# 4. Map the explicit entry point and initial linear flow
workflow.set_entry_point("ingestion")
workflow.add_edge("ingestion", "analyst_brain")


# 5. Inject the True ReAct Autonomous Loop Condition
# After the analyst speaks, the edge evaluates the ledger and jumps between tools or routes to auditing.
workflow.add_conditional_edges(
    "analyst_brain",
    react_router_edge,
    {
        "call_tools": "tools_runner",    # Routes alternative jumps to the tool execution layer
        "end_loop": "compliance_auditor" # Breaks out to final regulatory compliance evaluation
    }
)

# 6. Connect the tool loop-back edge
# Once the tools runner finishes its task, it writes the answer to the ledger and loops directly back to the analyst
workflow.add_edge("tools_runner", "analyst_brain")

# 7. Route the final node output directly to the explicit terminal graph end marker
workflow.add_edge("compliance_auditor", END)


# 8. Compile the layout architecture into a functional executable state machine runtime
compiled_graph = workflow.compile()































