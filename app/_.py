import json
from langchain_core.tools import tool

@tool
def check_internal_blacklist_registry(pan_card: str) -> str:
    """
    Queries corporate bank security database registries to check if an Indian PAN card is flagged for historical fraud or severe defaults.
    
    Args:
        pan_card (str): The validated 10-character alphanumeric Indian PAN card string.
        
    Returns:
        str: A JSON string containing the security clearing status and explicit matching reasons.
    """
    # Authentic simulation of an enterprise secure credit database registry lookup
    flagged_registry = ["ABCDE1234F", "XYZPT9876Q", "MNOVB4567Z"]
    normalized_pan = pan_card.strip().upper()
    
    if normalized_pan in flagged_registry:
        return json.dumps({
            "status": "FLAGGED", 
            "reason": "Severe historical credit default, willful non-performing asset (NPA) match, or active fraud registry alert flag."
        })
    return json.dumps({
        "status": "CLEARED", 
        "reason": "No regulatory or banking safety blacklist registry flags detected for this permanent account identifier."
    })

@tool
def calculate_financial_ratios(monthly_income: float, existing_debt: float, requested_amount: float, collateral_value: float) -> str:
    """
    Calculates the critical Debt-to-Income (DTI) exposure limits and Loan-to-Value (LTV) collateral buffers for banking risk underwriting.
    
    Args:
        monthly_income (float): Gross monthly verified income or business turnover.
        existing_debt (float): Existing cumulative monthly EMI obligations.
        requested_amount (float): Principal capital requested in the new application.
        collateral_value (float): Fair market valuation of the pledged security assets.
        
    Returns:
        str: A JSON string detailing computed percentages and specific safety risk threshold breaches.
    """
    # Indian Banking Simulation: Assume a standard 2% monthly structural debt repayment factor on the principal loan amount
    simulated_new_emi = requested_amount * 0.02
    total_projected_monthly_debt = existing_debt + simulated_new_emi
    
    # Precise ratio computations
    dti_percentage = round((total_projected_monthly_debt / monthly_income) * 100, 2) if monthly_income > 0 else 100.0
    ltv_percentage = round((requested_amount / collateral_value) * 100, 2) if collateral_value > 0 else 100.0
    
    return json.dumps({
        "debt_to_income_ratio_percentage": dti_percentage,
        "loan_to_value_ratio_percentage": ltv_percentage,
        "is_dti_critical": dti_percentage > 45.0, # 45% represents the standard conservative retail bank risk ceiling
        "is_ltv_safe": ltv_percentage <= 80.0     # 80% represents the maximum standard collateralized exposure safety boundary
    })

@tool
def evaluate_vintage_eligibility(employment_type: str, vintage_years: float) -> str:
    """
    Evaluates the active business operational tenure or continuous professional employment timeline against minimum threshold boundaries.
    
    Args:
        employment_type (str): The normalized framework string, strictly either 'Business' or 'Salaried'.
        vintage_years (float): The continuous tenure length tracked in years.
        
    Returns:
        str: A JSON string containing the required compliance baselines and explicit stability clearance status.
    """
    normalized_type = employment_type.strip().lower()
    
    # Regulatory compliance rules: Active businesses require a longer continuous operational baseline than salaried workers
    required_years = 3.0 if normalized_type == "business" else 1.5
    is_approved = vintage_years >= required_years
    
    return json.dumps({
        "required_tenure_years": required_years,
        "actual_vintage_years": vintage_years,
        "vintage_stability_approved": is_approved
    })

































