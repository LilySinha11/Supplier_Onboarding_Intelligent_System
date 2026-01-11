import os
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph_flow.state import SupplierState

from agents.screening_agent import run as screening_run
from agents.risk_agent import run as risk_run
from agents.document_agent import run as document_run
from agents.financial_agent import run as financial_run

graph = StateGraph(SupplierState)

# -------------------
# Nodes
# -------------------
graph.add_node("screening", screening_run)
graph.add_node("risk", risk_run)
graph.add_node("documents", document_run)
graph.add_node("financial", financial_run)

# -------------------
# Entry
# -------------------
graph.set_entry_point("screening")

# -------------------
# Linear flow
# -------------------
graph.add_edge("screening", "risk")

# After RISK → decide whether to stop or continue
def route_after_risk(state):
    # Always go to documents after risk
    return "documents"

graph.add_conditional_edges(
    "risk",
    route_after_risk,
    {
        "documents": "documents"
    }
)

# After DOCUMENTS → pause OR go to financial
def route_after_documents(state):
    if state["workflow_status"] == "PAUSED":
        return END    # Stop graph, UI will show upload screen
    return "financial"

graph.add_conditional_edges(
    "documents",
    route_after_documents,
    {
        END: END,
        "financial": "financial"
    }
)

# Financial always ends
graph.add_edge("financial", END)

# -------------------
# Compile
# -------------------
onboarding_graph = graph.compile()
