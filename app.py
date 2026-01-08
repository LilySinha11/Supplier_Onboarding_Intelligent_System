import os
from flask import Flask, render_template, request
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
# Create DB tables (run once)
# ----------------------------------------
with app.app_context():
    db.create_all()

# ----------------------------------------
# Supplier Registration Page
# ----------------------------------------
@app.route("/")
def register_page():
    return render_template("supplier_registeration.html")

# ----------------------------------------
# Scenario 1 → 2 → 3 → 4
# Screening → Risk → Documents → Intelligence
# ----------------------------------------
@app.route("/screening/start", methods=["POST"])
def start_screening():

    # ✅ FULLY INITIALIZED STATE (VERY IMPORTANT)
    state = {
        "supplier_id": 1,
        "supplier_name": request.form["supplier_name"],
        "country": request.form["country"],
        "category": request.form["category"],

        # Scenario 1
        "screening_status": "",
        "pre_qualification_score": 0.0,

        # Scenario 2
        "risk_score": 0.0,
        "risk_level": "",
        "risk_explanation": "",
        "risk_sources": [],

        # Scenario 3 / 4 (DOCUMENTS)
        "document_status": {"uploaded": []},
        "document_extraction": {},
        "document_validation": {
            "expired": [],
            "name_consistent": True
        },
        "document_score": None,
        "document_alerts": [],

        # Workflow
        "workflow_status": "RUNNING",
        "current_stage": "screening",
        "pause_reason": "",

        # Logs
        "agent_logs": []
    }

    # ▶️ Run LangGraph
    result = onboarding_graph.invoke(state)

    # 💾 Persist state
    onboarding_state = OnboardingState(
        supplier_id=state["supplier_id"],
        state_json=result,
        current_stage=result.get("current_stage"),
        status=result.get("workflow_status"),
        pause_reason=result.get("pause_reason"),
        screening_status=result.get("screening_status"),
        pre_qualification_score=result.get("pre_qualification_score")
    )

    db.session.add(onboarding_state)
    db.session.commit()

    # ✅ ALWAYS show Screening + Risk result first
    return render_template(
        "screening_result.html",
        result=result
    )

# ----------------------------------------
# Scenario 3 / 4: Document Upload + Intelligence
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

        # Reset workflow for resume
        state["workflow_status"] = "RUNNING"
        state["pause_reason"] = ""
        state["agent_logs"] = []

        # ▶️ Resume LangGraph
        result = onboarding_graph.invoke(state)

        # Persist updated state
        record.state_json = result
        record.current_stage = result.get("current_stage")
        record.status = result.get("workflow_status")
        record.pause_reason = result.get("pause_reason")
        db.session.commit()

        if result.get("workflow_status") == "COMPLETED":
            result["pause_reason"] = ""


        # 🔴 STILL PAUSED → stay on upload page
        if result.get("workflow_status") == "PAUSED":
            return render_template(
                "upload_documents.html",
                pause_reason=result.get("pause_reason"),
                state=result
            )

        # ✅ COMPLETED → show document intelligence
        return render_template(
            "document_intelligence.html",
            result=result
        )

    # --------------------
    # GET → Show upload page
    # --------------------
    return render_template(
        "upload_documents.html",
        pause_reason=record.pause_reason,
        state=state
    )

# ----------------------------------------
# App Runner
# ----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
