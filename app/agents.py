import os
import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.tools import (
    calculate_financial_ratios,
    check_internal_blacklist_registry,
    evaluate_vintage_eligibility
)
from app.rag_engine import execute_advanced_rag_lookup


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

tools_list = [calculate_financial_ratios, check_internal_blacklist_registry, evaluate_vintage_eligibility]
llm_with_tools = llm.bind_tools(tools_list)

async def data_ingestion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Acts as the entry gate to the graph. Extracts user metrics from the state ledger
    and injects the system prompt boundaries and initial instructions.
    """
    profile = state["client_profile"]

    system_instruction = SystemMessage(content = (
        "You are the Aegis Core Financial Analyst Agent, powered by Gemini 2.5 Flash.\n"
        "Your role is to completely audit incoming loan applications for Indian retail and MSME clients.\n"
        "You have access to tools for checking blacklists, calculating financial ratios, and verifying operational vintage.\n"
        "CRITICAL: Do not attempt to calculate ratios or guess security statuses yourself. You MUST call your tools"
        "to gather observations before rendering an underwriting systhesis. Keep calling tools until you have all the facts."
    ))

    initial_prompt = HumanMessage(content=(
        f"Begin full autonomous risk underwriting audit for the following client profile: {json.dumps(profile)}.\n"
        "Review this profile, determine which tools are required to verify the risk factors, and execute them."
    ))

    return {
        "current_node": "DATA_INGESTION",
        "messages": [system_instruction, initial_prompt],
        "execution_logs": ["System: Data ingestion completed. Seeding state vectors..."]
    }

async def financial_analyst_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure cognitive reasoning node. Reads the message history ledger from the state,
    invokes Gemini 2.5 Flash, and appends the model's structural text intent or tool request signatures.
    """
    messages_history = state["messages"]

    response = await llm_with_tools.ainvoke(messages_history)

    if response.tool_calls:
        requested_tools = [tool['name'] for tool in response.tool_calls]
        log_msg = f"🤖 [Analyst Decision]: Context ledger requires execution of tools: {requested_tools}"
    else:
        log_msg = f"🧠 [Analyst Synthesis]: {response.content}"
        
    return {
        "current_node": "FINANCIAL_ANALYST_AGENT",
        "messages": [response],
        "execution_logs": [log_msg]
    }


