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
    


