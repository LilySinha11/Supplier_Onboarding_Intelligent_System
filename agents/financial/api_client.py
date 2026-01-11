import requests
import os

FMP_API_KEY = os.getenv("FMP_API_KEY")

def safe_first(url):
    r = requests.get(url)
    data = r.json()

    if isinstance(data, list) and len(data) > 0:
        return data[0]

    return None


def get_balance_sheet(symbol):
    return safe_first(
        f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=1&apikey={FMP_API_KEY}"
    )

def get_income_statement(symbol):
    return safe_first(
        f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=1&apikey={FMP_API_KEY}"
    )

def get_cashflow(symbol):
    return safe_first(
        f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit=1&apikey={FMP_API_KEY}"
    )
