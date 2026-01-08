from agents.documents.extractors.mock_extractor import extract as extract_text
from agents.documents.extractors.groq_extractor import extract_fields_with_groq
from agents.documents.validators.expiry_validator import is_expired
from agents.documents.validators.consistency_validator import is_name_consistent
from agents.documents.scorer import compute_score

REQUIRED_DOCS = {"GST", "PAN", "ISO"}

def run(state):
    state["current_stage"] = "documents"
    state["agent_logs"].append("Starting document intelligence agent")

    # ALWAYS initialize document fields (CRITICAL)
    state.setdefault("document_extraction", {})
    state.setdefault("document_validation", {"expired": [], "name_consistent": True})
    state.setdefault("document_score", None)
    state.setdefault("document_alerts", [])

    uploaded = set(state.get("document_status", {}).get("uploaded", []))
    missing = sorted(REQUIRED_DOCS - uploaded)

    # 🔴 BLOCK if documents missing
    if missing:
        state["workflow_status"] = "PAUSED"
        state["pause_reason"] = f"Missing documents: {', '.join(missing)}"
        state["document_alerts"] = missing

        state["agent_logs"].append(
            f"Paused – missing documents: {', '.join(missing)}"
        )
        return state

    # ✅ All docs uploaded → attempt extraction
    extracted = {}
    expired_docs = []

    try:
        for doc in sorted(uploaded):
            # 1️⃣ OCR
            raw_text = extract_text(doc)

            # 2️⃣ LLM extraction
            fields = extract_fields_with_groq(raw_text)

            extracted[doc] = fields

            if is_expired(fields.get("expiry_date")):
                expired_docs.append(doc)

    except Exception as e:
        # 🔥 HARD FAIL → PAUSE SAFELY
        state["workflow_status"] = "PAUSED"
        state["pause_reason"] = "Document extraction failed. Please retry later."
        state["document_alerts"] = ["OCR/Extraction error"]

        state["agent_logs"].append(f"OCR failure: {str(e)}")
        return state

    # 🧠 Cross-document validation
    name_consistent = is_name_consistent(
        extracted, state["supplier_name"]
    )

    score = compute_score(expired_docs, name_consistent)

    # ✅ SUCCESS
    state["document_extraction"] = extracted
    state["document_validation"] = {
        "expired": expired_docs,
        "name_consistent": name_consistent
    }
    state["document_score"] = score
    state["document_alerts"] = expired_docs

    state["workflow_status"] = "COMPLETED"
    state["pause_reason"] = ""

    state["agent_logs"].append("Document intelligence completed successfully")

    return state
