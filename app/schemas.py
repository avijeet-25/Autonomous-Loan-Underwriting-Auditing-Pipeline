from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
import re

class LoanApplicationSchema(BaseModel):

    applicant_id: str = Field(..., description = "Unique alphanumeric identifier for the client")
    client_name: str = Field(..., description = "Legal name of the individual or corporate entity")
    employment_type: Literal["SALARIED", "BUSINESS"] = Field(..., description = "Primary income source type")

    monthly_income_or_turnover: float = Field(..., gt=0, description = "Verified monthly salary or business monthly turnover in INR")
    existing_debt: float = 