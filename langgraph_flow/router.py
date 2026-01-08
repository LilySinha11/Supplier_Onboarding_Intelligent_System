def route(state):
    if state.get("workflow_status") == "PAUSED":
        return "END"
    return state["current_stage"]
