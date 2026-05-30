from typing import TypedDict, Annotated, Sequence, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    """
    The unified state object passed between all nodes in our LangGraph pipeline.
    Uses Annotated[..., add] to continuously append incoming messages and logs
    without overwriting historical execution traces.
    """

    client_profile: Dict[str, Any]

    messages: Annotated[Sequence[BaseMessage], add]

    current_node: str
    underwriting_metrics: Dict[str, Any]
    blacklist_status: str
    vintage_status: str
    final_verdict: str 

    execution_logs: Annotated[list[str], add]


