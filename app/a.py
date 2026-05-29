from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
import re

class LoanApplicationSchema(BaseModel):
    # Basic Profile
    applicant_id: str = Field(..., description="Unique alphanumeric identifier for the client")
    client_name: str = Field(..., description="Legal name of the individual or corporate entity")
    employment_type: Literal["SALARIED", "BUSINESS"] = Field(..., description="Primary income source type")
    
    # Financial & Scale Metrics
    monthly_income_or_turnover: float = Field(..., gt=0, description="Verified monthly salary or business monthly turnover in INR")
    existing_debt: float = Field(..., ge=0, description="Total current monthly EMIs and debt obligations in INR")
    requested_amount: float = Field(..., gt=0, description="Loan principal amount requested")
    collateral_value: float = Field(..., ge=0, description="Market value of pledged assets in INR")
    business_vintage_years: float = Field(..., ge=0, description="Years of active operational history or job continuous tenure")
    
    # Risk & Compliance Parameters
    cibil_score: int = Field(..., ge=300, le=900, description="Bureau credit rating (CIBIL score)")
    has_past_default_history: bool = Field(..., description="True if the client was ever a defaulter in any previous loan")
    
    # Document Verification Keys
    national_id_pan: str = Field(..., description="Permanent Account Number (PAN) of the client")
    itr_filed_status: bool = Field(..., description="Whether Income Tax Return filings are attached and verified")

    # 1. Field Validator: Enforcing Indian PAN Card Format Regex
    @field_validator('national_id_pan')
    @classmethod
    def validate_pan_format(cls, v: str) -> str:
        pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        cleaned_pan = v.strip().upper()
        if not re.match(pan_regex, cleaned_pan):
            raise ValueError("Invalid PAN format. Must match standard Indian PAN pattern (e.g., ABCDE1234F).")
        return cleaned_pan

    # 2. Model-Level Validator: Complex Cross-Field Business Logic
    @model_validator(mode='after')
    def verify_financial_logic(self) -> 'LoanApplicationSchema':
        # Rule A: Prevent input data anomalies where debt exceeds income
        if self.existing_debt > self.monthly_income_or_turnover:
            raise ValueError("Data Anomaly: Total existing monthly debt cannot exceed monthly income/turnover.")
        
        # Rule B: Compliance gate - If they have a default history, make sure collateral is provided
        if self.has_past_default_history and self.collateral_value <= 0:
            raise ValueError("Risk Compliance Violation: Clients with past default history MUST pledge collateral assets.")
            
        return self