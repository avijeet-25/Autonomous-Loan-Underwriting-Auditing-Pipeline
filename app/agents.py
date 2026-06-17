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
    google_api_key="AIzaSyCoMqC2FknWg8wR_JGhpAyYq23c2Gf_tVY"
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
        "to gather observations before rendering an underwriting synthesis. Keep calling tools until you have all the facts."
        "CRITICAL: Call exactly ONE tool per response. Never call multiple tools in the same response. "
        "After each tool result, inspect the updated ledger and then decide the next single tool if needed. "
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
    messages_history = state.get("messages", [])

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


async def compliance_auditor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Advanced RAG Agent node. It executes after the analyst's tool loop finishes.
    Queries the local FAISS index for relevant policy clauses and synthesizes a structured verdict.
    """
    profile = state["client_profile"]
    messages_history = state.get("messages", [])

    history_string = str([str(m.content) for m in messages_history]).lower()

    rag_query = f"Underwriting threshold rules regarding a CIBIL score of {profile['cibil_score']} and mandatory ITR filing verification."

    reranked_policy_clauses = execute_advanced_rag_lookup(query=rag_query, top_k_vector=4, top_n_rerank=2)

    auditor_prompt = (
        f"You are the Aegis Lead Compliance Auditor Agent. Your job is to verify if this applicant matches our official policies.\n\n"
        f"--- APPLICANT LOGGED METRICS (FROM STATE LEDGER) ---\n"
        f"CIBIL Bureau Score: {profile['cibil_score']}\n"
        f"Income Tax Returns (ITR) Filed Status: {profile['itr_filed_status']}\n"
        f"Full Historical Tool Execution Logs: {history_string}\n\n"
        f"--- RETRIEVED GROUND-TRUTH REGULATORY CLAUSES (RERANKED) ---\n"
        f"Clause 1: {reranked_policy_clauses[0]}\n"
        f"Clause 2: {reranked_policy_clauses[1]}\n\n"
        f"--- INSTRUCTIONS ---\n"
        f"Cross-verify the logged metrics against the retrieved regulatory clauses.\n"
        f"Output a JSON object with exactly two keys:\n"
        f"1. 'verdict': string, either 'APPROVED' or 'REJECTED'\n"
        f"2. 'reason': A precise sentence explaining the compliance justification based strictly on the clauses.\n"
        f"Respond ONLY with raw JSON. Remove any markdown block indicators like ```json."
    )

    response = await llm.ainvoke([HumanMessage(content=auditor_prompt)])

    try:
        clean_json = response.content.replace("```json","").replace("```","").strip()
        parsed_data = json.loads(clean_json)
        verdict = parsed_data.get("verdict", "REJECTED").upper()
        reason = parsed_data.get("reason", "Application failed to clear underwriting constraints.")
    except Exception:
        verdict = "REJECTED"
        reason = "System Failure: Failed to parse clean structured JSON compliance matrix from model output."


    return {
        "current_node": "COMPLIANCE_AUDITOR_AGENT",
        "final_verdict": verdict,
        "messages": [response],
        "execution_logs": [
            "🔍 FAISS Index: Contextual vector lookup completed.",
            "⚡ Cross-Encoder: Rerank verification scored context successfully.",
            f"⚖️ [Auditor Summary]: {reason}",
            f"System: Final underwriting verdict locked as [{verdict}]."
        ]
    }