from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

from config import Config
from extensions import db
from langgraph_flow.graph import onboarding_graph
from models.onboarding_state import OnboardingState

# ----------------------------------------
# App Setup
# ----------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------------------------------
# Create DB tables
# ----------------------------------------
with app.app_context():
    db.create_all()

# ----------------------------------------
# Supplier Registration
# ----------------------------------------
@app.route("/")
def register_page():
    return render_template("supplier_registration.html")

# ----------------------------------------
# Start Onboarding (Scenario 1 → 2 → 3)
# ----------------------------------------
@app.route("/screening/start", methods=["POST"])
def start_screening():

    state = {
        "supplier_id": 1,
        "supplier_name": request.form["supplier_name"],
        "country": request.form["country"],
        "category": request.form["category"],

        "screening_status": "",
        "pre_qualification_score": 0.0,

        "risk_score": 0.0,
        "risk_level": "",
        "risk_explanation": "",
        "risk_sources": [],

        "document_status": {"uploaded": []},
        "document_extraction": {},
        "document_validation": {"expired": [], "name_consistent": True},
        "document_score": None,
        "document_alerts": [],

        "financial_score": None,
        "credit_recommendation": "",
        "financial_metrics": {},

        "workflow_status": "RUNNING",
        "current_stage": "screening",
        "pause_reason": "",
        "agent_logs": []
    }

    # Run LangGraph ONCE
    result = onboarding_graph.invoke(state)

    # Persist
    onboarding_state = OnboardingState(
        supplier_id=1,
        state_json=result,
        current_stage=result.get("current_stage"),
        status=result.get("workflow_status"),
        pause_reason=result.get("pause_reason"),
        screening_status=result.get("screening_status"),
        pre_qualification_score=result.get("pre_qualification_score")
    )
    db.session.add(onboarding_state)
    db.session.commit()

    # 🔥 ALWAYS show screening + risk first
    return render_template("screening_result.html", result=result)

# ----------------------------------------
# Scenario 3 + 4 → Upload Documents & Resume
# ----------------------------------------
@app.route("/documents/upload", methods=["GET", "POST"])
def upload_documents():

    record = OnboardingState.query.order_by(OnboardingState.id.desc()).first()
    state = record.state_json

    # --------------------
    # POST → Upload & Resume
    # --------------------
    if request.method == "POST":

        uploaded = state["document_status"]["uploaded"]

        for doc_type in ["GST", "PAN", "ISO"]:
            file = request.files.get(doc_type)
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_DIR, filename))
                if doc_type not in uploaded:
                    uploaded.append(doc_type)

        # Reset workflow
        state["workflow_status"] = "RUNNING"
        state["pause_reason"] = ""
        state["agent_logs"] = []

        # 🚨 CRITICAL: Resume from DOCUMENTS, not from SCREENING
        result = onboarding_graph.invoke(
            state,
            config={"configurable": {"start_at": "documents"}}
        )

        # Persist
        record.state_json = result
        record.current_stage = result.get("current_stage")
        record.status = result.get("workflow_status")
        record.pause_reason = result.get("pause_reason")
        db.session.commit()

        # 🔴 Still blocked
        if result["workflow_status"] == "PAUSED":
            return render_template(
                "upload_documents.html",
                pause_reason=result["pause_reason"],
                state=result
            )

        # 🟢 Financial done → render directly
        if result["current_stage"] == "financial":
            return render_template("financial_result.html", result=result)

        # Otherwise show doc intelligence
        return render_template("document_intelligence.html", result=result)

    # --------------------
    # GET → Show upload screen
    # --------------------
    return render_template(
        "upload_documents.html",
        pause_reason=record.pause_reason,
        state=state
    )


# ----------------------------------------
# Scenario 4 – Financial Result
# ----------------------------------------
@app.route("/financial")
def financial_result():

    record = OnboardingState.query.order_by(OnboardingState.id.desc()).first()
    state = record.state_json

    return render_template("financial_result.html", result=state)

# ----------------------------------------
# App Runner
# ----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
