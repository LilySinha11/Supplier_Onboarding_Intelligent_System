import os
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph_flow.state import SupplierState
from agents.screening_agent import run as screening_run
from agents.risk_agent import run as risk_run
from agents.document_agent import run as document_run

graph = StateGraph(SupplierState)

graph.add_node("screening", screening_run)
graph.add_node("risk", risk_run)
graph.add_node("documents", document_run)

graph.set_entry_point("screening")

graph.add_edge("screening", "risk")
graph.add_edge("risk", "documents")

# If PAUSED, LangGraph will naturally stop; otherwise END
graph.add_edge("documents", END)

onboarding_graph = graph.compile()

