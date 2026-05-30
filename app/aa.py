from typing import Dict, Any
import json
from app.tools import (
    calculate_financial_ratios, 
    check_internal_blacklist_registry, 
    evaluate_vintage_eligibility
)

# 1. Concrete Implementation of the Data Ingestion Node
async def data_ingestion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads the initial client profile payload, executes the database blacklist check,
    and initializes our structural state logs.
    """
    profile = state["client_profile"]
    pan_card = profile["national_id_pan"]
    
    # Execute our specialized blacklist lookup tool "with its own hands"
    blacklist_tool_result = check_internal_blacklist_registry.invoke({"pan_card": pan_card})
    blacklist_data = json.loads(blacklist_tool_result)
    
    logs = [
        f"Data Ingestion: Schema parsed for applicant {profile['client_name']}.",
        f"Security Check: Blacklist query returned status [{blacklist_data['status']}]."
    ]
    
    return {
        "current_node": "DATA_INGESTION",
        "blacklist_status": blacklist_data["status"],
        "execution_logs": logs
    }


# 2. Concrete Implementation of the Financial Analyst Agent Node (ReAct)
async def financial_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a ReAct reasoning loop. The agent evaluates data parameters, 
    calls financial math tools to process credit risk, and checks structural tenure.
    """
    profile = state["client_profile"]
    
    # Step 1: Execute financial ratio tool calculations
    ratio_result = calculate_financial_ratios.invoke({
        "monthly_income": profile["monthly_income_or_turnover"],
        "existing_debt": profile["existing_debt"],
        "requested_amount": profile["requested_amount"],
        "collateral_value": profile["collateral_value"]
    })
    metrics = json.loads(ratio_result)
    
    # Step 2: Execute stability vintage assessment tool
    vintage_result = evaluate_vintage_eligibility.invoke({
        "employment_type": profile["employment_type"],
        "vintage_years": profile["business_vintage_years"]
    })
    vintage_data = json.loads(vintage_result)
    
    # Simulating the ReAct agent's cognitive "Thought & Decision" process
    thought_log = (
        f"🧠 [Analyst Thought]: Applicant CIBIL score is {profile['cibil_score']}. "
        f"Calculated Debt-to-Income (DTI) is {metrics['debt_to_income_ratio_percentage']}%. "
        f"Operational vintage stability is validated as {vintage_data['vintage_stability_approved']}."
    )
    
    logs = [
        "Financial Analyst Agent: Booting analytical framework runtime...",
        thought_log,
        f"Metrics Applied: DTI Critical Status = {metrics['is_dti_critical']} | LTV Safe Status = {metrics['is_ltv_safe']}"
    ]
    
    return {
        "current_node": "FINANCIAL_ANALYST_AGENT",
        "underwriting_metrics": metrics,
        "vintage_status": "APPROVED" if vintage_data["vintage_stability_approved"] else "FAILED",
        "execution_logs": logs
    }


# 3. Concrete Implementation of the Compliance Auditor Node (Advanced RAG Simulation)
async def compliance_auditor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a two-stage Advanced RAG lookup against policy frameworks. 
    Simulates vector database context retrieval followed by a Reranker filtering layer.
    """
    profile = state["client_profile"]
    metrics = state.get("underwriting_metrics", {})
    
    # Simulating a vector database retrieval action for compliance rules
    vector_retrieval_log = "🔍 VectorDB Retrieval: Fetching text chunks matching query 'RBI credit exposure ceiling limits'..."
    reranker_log = "⚡ Reranker Model (FlashRank): Re-scoring 10 retrieved chunks down to top 2 highly relevant clauses."
    
    # Strict automated underwriting governance evaluation
    policy_approved = True
    rejection_reasons = []
    
    if profile["cibil_score"] < 650:
        policy_approved = False
        rejection_reasons.append("CIBIL score below standard corporate minimum risk threshold (650).")
        
    if metrics.get("is_dti_critical", False):
        policy_approved = False
        rejection_reasons.append("Debt-to-Income ratio exceeds maximum permissible exposure cap (45%).")
        
    if state.get("vintage_status") == "FAILED":
        policy_approved = False
        rejection_reasons.append("Operational vintage/tenure fails stability compliance thresholds.")
        
    if not profile["itr_filed_status"]:
        policy_approved = False
        rejection_reasons.append("Regulatory Compliance Deficit: Missing verified Income Tax Returns.")

    decision_summary = "Compliance Audit: All structural risk vector clauses passed regulatory filters." if policy_approved else f"Compliance Alert: Underwriting criteria breached. Violations: {'; '.join(rejection_reasons)}"
    
    logs = [
        vector_retrieval_log,
        reranker_log,
        f"🧠 [Auditor Thought]: Cross-referencing bureau history against retrieved risk vectors. Verdict ready.",
        decision_summary
    ]
    
    return {
        "current_node": "COMPLIANCE_AUDITOR_AGENT",
        "final_verdict": "APPROVED" if policy_approved else "REJECTED",
        "execution_logs": logs
    }


# 4. Concrete Implementation of the Final Execution Node
async def final_execution_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Finalizes the transaction state. Evaluates structural overrides, flags early 
    short-circuits (like blacklisted entries), and commits the decision record.
    """
    verdict = state.get("final_verdict", "PENDING")
    blacklist = state.get("blacklist_status", "CLEARED")
    
    # High-priority short-circuit check: Blacklisted entries are immediately overridden to REJECTED
    if blacklist == "FLAGGED":
        verdict = "REJECTED"
        log_message = "🔴 CRITICAL TERMINATION: Application summarily denied due to early security blacklist registry match."
    elif verdict == "APPROVED":
        log_message = "🟢 APPLICATION STATUS: APPROVED. Underwriting pipeline processed successfully. Dispatched system webhooks."
    else:
        log_message = "🔴 APPLICATION STATUS: REJECTED. Failed to satisfy baseline core underwriting validation criteria."
        
    return {
        "current_node": "EXECUTION_NODE",
        "final_verdict": verdict,
        "execution_logs": [log_message, "System Layer: Global state sequence finalized. Core pipeline connection closed."]
    }