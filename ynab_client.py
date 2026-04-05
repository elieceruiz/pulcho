# ynab_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.ynab.com/v1"

YNAB_API_KEY = os.getenv("YNAB_API_KEY")
YNAB_BUDGET_ID = os.getenv("YNAB_BUDGET_ID")


def get_transactions():
    if not YNAB_API_KEY or not YNAB_BUDGET_ID:
        raise Exception("Faltan variables de entorno de YNAB")

    url = f"{BASE_URL}/budgets/{YNAB_BUDGET_ID}/transactions"

    headers = {
        "Authorization": f"Bearer {YNAB_API_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error YNAB: {response.status_code} - {response.text}")

    return response.json()["data"]["transactions"]