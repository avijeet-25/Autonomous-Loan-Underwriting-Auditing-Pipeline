from langchain_core.tools import tool
import json

@tool
def calculate_financial_ratios(monthly_income: float, existing_debt: float, requested_amount: float, collateral_value: float) -> str:
    """
    Calculates crucial banking risk metrics: Debt-to-Income (DTI) ratio and Loan-to-Value (LTV) ratio.
    Use this tool whenever you need to evaluate financial viability or asset leverage.
    """
    try:
        
        dti_ratio = (existing_debt / monthly_income) * 100 if monthly_income > 0 else 100.0

        ltv_ratio = (requested_amount / collateral_value) * 100 if collateral_value > 0 else 100.0

        metrics = {
            "debt_to_income_ratio_percentage": round(dti_ratio, 2),
            "loan_to_value_ratio_percentage": round(ltv_ratio, 2),
            "is_dti_critical": dti_ratio > 45.0,
            "is_ltv_safe": ltv_ratio <= 80.0
        }

        return json.dumps(metrics)
    except Exception as e:
        return f"Error executing mathematical calculations: {str(e)}"
    

@tool
def check_internal_blacklist_registry(pan_card: str) -> str:
    """
    Queries the secure database registry to see if the client's PAN card matches
    historical corporate defaults, fraud lists, or operational blacklists.
    """

    mock_blacklist_ledger = [
        "ABCDE1234F",
        "XYZST9876Q"
    ]

    cleaned_pan = pan_card.strip().upper()

    if cleaned_pan in mock_blacklist_ledger:
        record = {
            "pan_card": cleaned_pan,
            "status": "FLAGGED",
            "reason": "Severe compliance alert: Entity flagged in internal recovery database for historical asset write-off."
        }
    else:
        record = {
            "pan_card": cleaned_pan,
            "status": "CLEARED",
            "reason": "No historical non-performing asset (NPA) or fraud matches found in corporate registry."
        }

    return json.dumps(record)


@tool
def evaluate_vintage_eligibility(employment_type: str, vintage_years: float) -> str:
    """
    Evaluates operational stability. checks if business operational history or continuous salary employement
    tenure meets corporate risk threshold requirements.
    """
    emp_upper = employment_type.strip().upper()

    threshold = 3.0 if emp_upper == "BUSINESS" else 1.0
    is_eligible = vintage_years >= threshold

    result = {
        "entity_type": emp_upper,
        "vintage_years_provided": vintage_years,
        "required_threshold_years": threshold,
        "vintage_stability_approved": is_eligible
    }

    return json.dumps(result)