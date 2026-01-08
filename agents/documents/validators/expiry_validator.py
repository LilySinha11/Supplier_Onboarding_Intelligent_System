from datetime import datetime

def is_expired(expiry_date: str) -> bool:
    try:
        return datetime.strptime(expiry_date, "%Y-%m-%d") < datetime.today()
    except Exception:
        return True
