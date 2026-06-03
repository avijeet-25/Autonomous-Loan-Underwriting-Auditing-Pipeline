from typing import Dict, Any
import json
from app.tools import (
    calculate_financial_ratios,
    check_internal_blacklist_registry,
    evaluate_vintage_eligibility
)


async def data_ingestion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads the initial client profile payload, executes the database blacklist check,
    and initializes our structural state logs.
    """
    profile = state["client_profile"]
    pan_card = profile["national_id_pan"]

    blacklist_tool_result = check_internal_blacklist_registry.invoke({"pan_card": pan_card})
    blacklist_data = json.loads(black_tool_result)

    logs = [
        f"Data Ingestion: Schema parsed for applicant {profile['client_name']}.",
        f"Security Check: Blacklist query returned status [{blacklist_data['status']}]."
    ]

    return {
        "current_node": "DATA_INGESTION",
        "blacklist_status": blacklist_data["status"],
        "execution_logs": logs
    }














