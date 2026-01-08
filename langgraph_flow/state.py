from typing import TypedDict, List, Dict


class SupplierState(TypedDict):
    # -----------------------
    # Supplier Identity
    # -----------------------
    supplier_id: int
    supplier_name: str
    country: str
    category: str

    # -----------------------
    # Scenario 1: Screening
    # -----------------------
    screening_status: str
    pre_qualification_score: float

    # -----------------------
    # Scenario 2: Risk Intelligence
    # -----------------------
    risk_score: float              # 0.0 – 1.0
    risk_level: str                # LOW / MEDIUM / HIGH
    risk_explanation: str
    risk_sources: List[str]

    # -----------------------
    # Scenario 3 & 4: Documents
    # -----------------------
    document_status: Dict          # uploaded docs
    document_extraction: Dict      # extracted fields
    document_validation: Dict      # expiry / consistency
    document_score: float
    document_alerts: List[str]

    # -----------------------
    # Workflow Control
    # -----------------------
    workflow_status: str           # RUNNING / PAUSED / COMPLETED
    current_stage: str             # screening / risk / documents
    pause_reason: str

    # -----------------------
    # Internal Logs (not UI)
    # -----------------------
    agent_logs: List[str]
