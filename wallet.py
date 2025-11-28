# wallet.py
import json
import os
from utils import sha256_hex

WALLET_FILE = "wallets.json"

# Simulated private keys (for educational demo).
# In a real system you'd never store plain private keys like this.
PRIVATE_KEYS = {
    "Alice": "ALICE_PRIVATE_SECRET_9b1",
    "Bob":   "BOB_PRIVATE_SECRET_3f7",
    "Charles": "CHARLES_PRIVATE_SECRET_z4y"
}

def load_wallets():
    if not os.path.exists(WALLET_FILE):
        return {}
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallets(wallets: dict):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def initialize_default_wallets():
    wallets = load_wallets()
    changed = False
    for user in ["Alice", "Bob", "Charles"]:
        if user not in wallets:
            wallets[user] = 1000.0
            changed = True
    if changed:
        save_wallets(wallets)
        print("Initialized default wallets: Alice, Bob, Charles → 1000 each")

def get_balance(user: str) -> float:
    wallets = load_wallets()
    return float(wallets.get(user, 0.0))

def credit_wallet(user: str, amount: float):
    wallets = load_wallets()
    wallets[user] = float(wallets.get(user, 0.0)) + float(amount)
    save_wallets(wallets)

def debit_wallet(user: str, amount: float) -> bool:
    wallets = load_wallets()
    if wallets.get(user, 0.0) < amount:
        return False
    wallets[user] = float(wallets.get(user, 0.0)) - float(amount)
    save_wallets(wallets)
    return True

def get_private_key(user: str) -> str:
    """Return the simulated private key for the user (if available)."""
    return PRIVATE_KEYS.get(user)
