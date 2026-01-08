from extensions import db
from datetime import datetime

class OnboardingState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer)

    state_json = db.Column(db.JSON)

    current_stage = db.Column(db.String(50))
    status = db.Column(db.String(20))       # RUNNING | PAUSED | COMPLETED
    pause_reason = db.Column(db.String(200))

    screening_status = db.Column(db.String(20))
    pre_qualification_score = db.Column(db.Float)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
