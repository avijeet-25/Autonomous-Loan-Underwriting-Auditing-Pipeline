from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any

class LoanApplicationSchema(BaseModel):
    client_name: str = Field(
        ..., 
        min_length=1,
        description="Legal business registration entity or individual applicant name"
    )
    national_id_pan: str = Field(
        ..., 
        min_length=10, 
        max_length=10,
        description="Indian Income Tax 10-character alphanumeric Permanent Account Number (PAN)"
    )
    cibil_score: int = Field(
        ..., 
        ge=300, 
        le=900, 
        description="Primary Credit Bureau Score Index (Strict regulatory limit between 300 and 900)"
    )
    monthly_income_or_turnover: float = Field(
        ..., 
        ge=0.0, 
        description="Gross monthly revenue, business turnover, or individual net salary verified in INR"
    )
    existing_debt: float = Field(
        ..., 
        ge=0.0, 
        description="Total cumulative current monthly EMI obligations across active credit facilities in INR"
    )
    requested_amount: float = Field(
        ..., 
        ge=0.0, 
        description="Principal loan capital requested by the entity in INR"
    )
    collateral_value: float = Field(
        ..., 
        ge=0.0, 
        description="Estimated current liquidation or fair market valuation of pledged security assets in INR"
    )
    employment_type: str = Field(
        ..., 
        description="Operational framework category: Must resolve strictly to 'Business' or 'Salaried'"
    )
    business_vintage_years: float = Field(
        ..., 
        ge=0.0, 
        description="Continuous operational tenure or uninterrupted professional employment history in years"
    )
    itr_filed_status: bool = Field(
        ..., 
        description="Explicit compliance flag: True if verified Income Tax Returns have been filed"
    )

    # ==========================================
    # 🛡️ PYDANTIC V2 FIELD-LEVEL VALIDATORS
    # ==========================================
    
    @field_validator('national_id_pan')
    @classmethod
    def validate_pan_format(cls, value: str) -> str:
        """Enforces the official, strict format layout of an Indian PAN card."""
        normalized = value.strip().upper()
        
        # Standard structural check: 5 letters, 4 numbers, 1 letter
        if not (normalized[:5].isalpha() and normalized[5:9].isdigit() and normalized[9].isalpha()):
            raise ValueError(
                "Invalid Indian PAN format. The structure must strictly follow "
                "5 uppercase letters, 4 sequential digits, and 1 ending letter (e.g., ABCDE1234F)."
            )
        return normalized

    @field_validator('employment_type')
    @classmethod
    def validate_employment_framework(cls, value: str) -> str:
        """Forces the input string to standardize cleanly to our explicit runtime tokens."""
        normalized = value.strip().capitalize() # Capitalizes first letter (e.g., "business" -> "Business")
        
        allowed_frameworks = ["Business", "Salaried"]
        if normalized not in allowed_frameworks:
            raise ValueError(
                f"Invalid employment framework classification '{value}'. "
                f"The value must resolve strictly to either 'Business' or 'Salaried'."
            )
        return normalized

    # ==========================================
    # 🛡️ PYDANTIC V2 MODEL-LEVEL VALIDATOR (Cross-Field)
    # ==========================================
    
    @model_validator(mode='after')
    def validate_financial_sanity_bounds(self) -> 'LoanApplicationSchema':
        """
        Executes cross-field macro evaluations to catch structural banking inconsistencies 
        before the data payload enters our LangGraph state ledger memory.
        """
        income = self.monthly_income_or_turnover
        debt = self.existing_debt
        
        # Critical Check 1: Prevent impossible debt obligations scenarios
        if debt > income and income > 0:
            raise ValueError(
                f"Financial Insanity Detected: Current existing monthly debt (INR {debt:,.2f}) "
                f"cannot exceed total gross monthly income (INR {income:,.2f})."
            )
            
        # Critical Check 2: Require collateral if requested loan amount is exceptionally large
        # If request > INR 15,00,000 and collateral is missing, short-circuit immediately
        if self.requested_amount > 1500000.0 and self.collateral_value == 0:
            raise ValueError(
                "Risk Governance Breach: Credit facilities exceeding INR 15,00,000 "
                "require a non-zero pledged collateral asset valuation to proceed."
            )
            
        return self

    # ==========================================
    # ⚙️ SCHEMA CONFIGURATION
    # ==========================================
    class Config:
        frozen = True  # Ensures data immutability within the state ledger
        json_schema_extra = {
            "example": {
                "client_name": "Rathore Logistics Indore",
                "national_id_pan": "ABCDE1234F",
                "cibil_score": 715,
                "monthly_income_or_turnover": 180000.0,
                "existing_debt": 30000.0,
                "requested_amount": 600000.0,
                "collateral_value": 900000.0,
                "employment_type": "Business",
                "business_vintage_years": 4.0,
                "itr_filed_status": True
            }
        }