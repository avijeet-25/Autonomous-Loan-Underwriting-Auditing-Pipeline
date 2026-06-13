import streamlit as st
import requests
import json

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Aegis Core Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Aegis: Autonomous Multi-Agent Underwriting Console")
st.caption("Enterprise Risk Evaluation Engine running LangGraph, Local FAISS RAG, and Gemini 2.5 Flash")
st.markdown("---")

# --- SIDEBAR CONFIGURATION & RISK PROFILE PRESETS ---
st.sidebar.header("📋 Risk Profiles & Presets")
profile_type = st.sidebar.selectbox(
    "Select Testing Matrix Template:",
    ["Manual Input", "Profile 1: High Risk Default", "Profile 2: Clear MSME Business", "Profile 3: Missing Document Baseline"]
)

# Seed realistic default testing values based on selection to make your demo run flawlessly
preset_data = {
    "client_name": "Indore Logistics Pvt Ltd",
    "national_id_pan": "ABCDE1234F",
    "cibil_score": 740,
    "monthly_income_or_turnover": 250000.0,
    "existing_debt": 40000.0,
    "requested_amount": 800000.0,
    "collateral_value": 1100000.0,
    "employment_type": "Business",
    "business_vintage_years": 4.5,
    "itr_filed_status": True
}

if profile_type == "Profile 1: High Risk Default":
    preset_data.update({
        "client_name": "Default High Risk Entity",
        "national_id_pan": "XYZPT9876Q",  # Blacklisted PAN string
        "cibil_score": 580,               # Failing bureau score
        "requested_amount": 1200000.0,
        "collateral_value": 0.0,          # Zero collateral breach
    })
elif profile_type == "Profile 2: Clear MSME Business":
    preset_data.update({
        "client_name": "Rathore Enterpises Indore",
        "national_id_pan": "PQRST5566A",
        "cibil_score": 780,
        "monthly_income_or_turnover": 450000.0,
        "existing_debt": 20000.0,
        "requested_amount": 1000000.0,
        "collateral_value": 2000000.0,
    })
elif profile_type == "Profile 3: Missing Document Baseline":
    preset_data.update({
        "client_name": "Anomalous Salaried Profile",
        "national_id_pan": "LMNVW9988Z",
        "cibil_score": 710,
        "itr_filed_status": False,        # Missing statutory ITR requirement
    })

# --- DATA ENTRY FORM INTERFACE ---
st.subheader("📝 Applicant Telemetry Parameters Entry Form")

col1, col2, col3 = st.columns(3)

with col1:
    client_name = st.text_input("Legal Entity / Applicant Name", value=preset_data["client_name"])
    national_id_pan = st.text_input("Indian Tax Identifier (PAN)", value=preset_data["national_id_pan"], max_chars=10)
    cibil_score = st.number_input("CIBIL Bureau Score Index", min_value=300, max_value=900, value=preset_data["cibil_score"])

with col2:
    monthly_income_or_turnover = st.number_input("Gross Monthly Revenue / Turnover (INR)", min_value=0.0, value=preset_data["monthly_income_or_turnover"])
    existing_debt = st.number_input("Current Active Monthly Debt EMIs (INR)", min_value=0.0, value=preset_data["existing_debt"])
    requested_amount = st.number_input("Requested Loan Principal Capital (INR)", min_value=0.0, value=preset_data["requested_amount"])

with col3:
    collateral_value = st.number_input("Pledged Collateral Asset Valuation (INR)", min_value=0.0, value=preset_data["collateral_value"])
    employment_type = st.selectbox("Employment / Framework Category", ["Business", "Salaried"], index=0 if preset_data["employment_type"] == "Business" else 1)
    business_vintage_years = st.number_input("Continuous Operational Tenure / Vintage (Years)", min_value=0.0, value=preset_data["business_vintage_years"])
    itr_filed_status = st.checkbox("Income Tax Returns (ITR) Verified Filed Status", value=preset_data["itr_filed_status"])

st.markdown("---")

# --- GRAPH STREAM EXECUTION DISPLAY LAYER ---
st.subheader("⚙️ Live Multi-Agent Execution Ledger Stream")
submit_btn = st.button("Submit Profile for Autonomous Underwriting Evaluation", type="primary")

if submit_btn:
    # 1. Package fields directly into a JSON payload corresponding to our validation schema
    payload = {
        "client_name": client_name,
        "national_id_pan": national_id_pan,
        "cibil_score": int(cibil_score),
        "monthly_income_or_turnover": float(monthly_income_or_turnover),
        "existing_debt": float(existing_debt),
        "requested_amount": float(requested_amount),
        "collateral_value": float(collateral_value),
        "employment_type": employment_type,
        "business_vintage_years": float(business_vintage_years),
        "itr_filed_status": bool(itr_filed_status)
    }

    # Create an empty container console block to stream out logs line-by-line smoothly
    console_block = st.empty()
    logs_accumulator = []
    
    # 2. Fire network connection to the FastAPI streaming server endpoint
    BACKEND_API_URL = "http://127.0.0.1:8000/api/v1/underwrite"
    
    try:
        with requests.post(BACKEND_API_URL, json=payload, stream=True) as response:
            if response.status_code == 500:
                st.error("Server Configuration Exception: Verify that your GOOGLE_API_KEY is successfully loaded.")
            elif response.status_code == 422:
                st.error("⚠️ Pydantic Validation Rejection: The input metrics violate our cross-field financial sanity rules.")
                st.json(response.json())
            elif response.status_code == 200:
                
                # Iterate line by line over the network raw bytes text-stream
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        
                        # Inspect the standard Server-Sent Event (SSE) prefix identifier
                        if decoded_line.startswith("data: "):
                            raw_json_str = decoded_line.replace("data: ", "").strip()
                            event_data = json.loads(raw_json_str)
                            
                            node_origin = event_data.get("node", "UNKNOWN_NODE")
                            log_status = event_data.get("status", "")
                            
                            # Standardize output string layout colorations using markdown tags
                            formatted_log = f"**[{node_origin}]** {log_status}"
                            logs_accumulator.append(formatted_log)
                            
                            # Join historical updates and render in an active visual scrolling ledger console block
                            console_block.markdown("\n\n".join(logs_accumulator))
                            
                            # Catch terminal states to draw high level layout status notification frames
                            if "Final underwriting verdict locked as [APPROVED]" in log_status:
                                st.success("🎉 Underwriting Clear: Application conforms fully to RBI policy standards.")
                            elif "Final underwriting verdict locked as [REJECTED]" in log_status:
                                st.error("❌ Application Rejected: Audit step failed compliance parameters.")
                            elif "Graph Runtime Aborted:" in log_status:
                                st.warning("⚠️ Processing Engine Interrupted.")
                                
    except Exception as network_err:
        st.error(f"Failed to communicate with Aegis Core Microservice Server at {BACKEND_API_URL}. Details: {str(network_err)}")












































        