from typing import TypedDict, Annotated, Sequence, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agents import data_ingestion_node, financial_analyst_agent, complilance_auditor_node
from app.tools import calculate_financial_ratios, check_internal_blacklist_registry, evaluate_vintage_eligibility

class AgentState(TypedDict):
    client_profile: Dict[str, Any]
    messages: Annotated[Sequence[BaseMessage], add]
    current_node: str
    final_verdict: str
    execution_logs: Annotated[list[str], add]


def react_router_edge(state: AgentState) -> str:
    """
    True agentic edge router. Inspects the final entry of the central ledger's message history.
    If Gemini 2.5 Flash outputted a 'tool_calls' token signature, it routes execution to the tool node.
    If Gemini outputted a standard text response, it breakes the loop and transitions to the auditor.
    """

    message_history = state["messages"]
    last_message = messages_history[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    
    return "end_loop"

workflow = StateGraph(AgentState)

workflow.add_node("ingestion", data_ingestion_node)
workflow.add_node("analyst_brain", financial_analyst_agent)
workflow.add_node("compliance_auditor", compliance_auditor_node)


functional_tools_node = ToolNode([
    calculate_financial_ratios,
    check_internal_blacklist_registry,
    evaluate_vintage_eligibility
])
workflow.add_node("tools_runner", functional_tools_node)

workflow.set_entry_point("ingestion")
workflow.add_edge("ingestion", "analyst_brain")

workflow.add_conditional_edges(
    "analyst_brain",
    react_router_edge,
    {
        "call_tools": "tools_runner",
        "end_loop": "compliance_auditor"
    }
)

workflow.add_edge("tools_runner", "analyst_brain")

workflow.add_edge("compliance_auditor", END)

compiled_graph = workflow.compile()