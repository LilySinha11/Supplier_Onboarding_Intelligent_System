from agents.documents.extractors.mock_extractor import extract as extract_text
from agents.documents.extractors.groq_extractor import extract_fields_with_groq
from agents.documents.validators.expiry_validator import is_expired
from agents.documents.validators.consistency_validator import is_name_consistent
from agents.documents.scorer import compute_score

REQUIRED_DOCS = {"GST", "PAN", "ISO"}


def run(state):
    # ------------------------------
    # Stage setup
    # ------------------------------
    state["current_stage"] = "documents"
    state["agent_logs"].append("📄 Starting Document Intelligence Agent")

    # ------------------------------
    # Safe initialization (CRITICAL)
    # ------------------------------
    state.setdefault("document_status", {"uploaded": []})
    state.setdefault("document_extraction", {})
    state.setdefault("document_validation", {"expired": [], "name_consistent": True})
    state.setdefault("document_score", None)
    state.setdefault("document_alerts", [])

    uploaded = set(state["document_status"].get("uploaded", []))
    missing = sorted(REQUIRED_DOCS - uploaded)

    # ------------------------------
    # 🚨 BLOCK if documents missing
    # ------------------------------
    if missing:
        state["workflow_status"] = "PAUSED"
        state["pause_reason"] = f"Missing documents: {', '.join(missing)}"
        state["document_alerts"] = missing

        state["agent_logs"].append(
            f"⏸ Workflow paused — missing documents: {', '.join(missing)}"
        )

        return state   # 🔴 LangGraph will stop here due to conditional edge

    # ------------------------------
    # 🧠 Extract + Validate
    # ------------------------------
    extracted = {}
    expired_docs = []

    try:
        for doc in sorted(uploaded):
            state["agent_logs"].append(f"📥 Reading {doc}")

            # 1️⃣ OCR / mock extraction
            raw_text = extract_text(doc)

            # 2️⃣ Groq field extraction (doc type REQUIRED)
            fields = extract_fields_with_groq(raw_text, doc)

            extracted[doc] = fields

            # 3️⃣ Expiry validation
            if is_expired(fields.get("expiry_date")):
                expired_docs.append(doc)

    except Exception as e:
        # Hard stop on OCR or LLM failure
        state["workflow_status"] = "PAUSED"
        state["pause_reason"] = "Document extraction failed. Please retry."
        state["document_alerts"] = ["OCR / LLM failure"]

        state["agent_logs"].append(f"❌ Document processing error: {str(e)}")
        return state

    # ------------------------------
    # 🧠 Cross-document validation
    # ------------------------------
    name_consistent = is_name_consistent(
        extracted,
        state.get("supplier_name")
    )

    score = compute_score(expired_docs, name_consistent)

    # ------------------------------
    # Store results
    # ------------------------------
    state["document_extraction"] = extracted
    state["document_validation"] = {
        "expired": expired_docs,
        "name_consistent": name_consistent
    }
    state["document_score"] = score
    state["document_alerts"] = expired_docs

    # ------------------------------
    # 🚦 DO NOT end workflow here
    # ------------------------------
    state["workflow_status"] = "RUNNING"
    state["pause_reason"] = ""

    state["agent_logs"].append("✅ Documents validated successfully → routing to Financial Agent")

    return state
