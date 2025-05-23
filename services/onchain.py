# services/onchain.py
import requests
import os

def get_onchain_activity(address="0xYourWallet"):
    key = os.getenv("COVALENT_API_KEY")
    url = f"https://api.covalenthq.com/v1/address/{address}/activity/?key={key}"
    return requests.get(url).json()
