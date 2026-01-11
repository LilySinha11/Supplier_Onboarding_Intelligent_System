import requests
import os

FMP_API_KEY = os.getenv("FMP_API_KEY")

def resolve_symbol(company_name):
    url = f"https://financialmodelingprep.com/api/v3/search?query={company_name}&limit=5&apikey={FMP_API_KEY}"
    data = requests.get(url).json()

    if not data:
        return None

    # Prefer Indian NSE stocks
    for item in data:
        if item.get("exchangeShortName") in ["NSE", "BSE"]:
            return item["symbol"]

    return data[0]["symbol"]
