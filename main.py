# main.py
from blockchain import Blockchain
from transaction import Transaction
from wallet import get_balance, load_wallets
import json

def show_menu():
    print("\n================= MENU =================")
    print("1) Create & Sign Transaction")
    print("2) Mine Block")
    print("3) View Blockchain (chain.json)")
    print("4) Validate Chain")
    print("5) View Wallet Balances")
    print("6) View Pending Transactions")
    print("7) Exit")
    print("========================================")

def pretty_print_chain(chain_file="chain.json"):
    try:
        with open(chain_file, "r") as f:
            chain = json.load(f)
    except:
        print("No chain found.")
        return
    for block in chain:
        print("\n--- Block", block["index"], "---")
        print("Timestamp:", block["timestamp"])
        print("PrevHash:", block["previous_hash"])
        print("Hash:", block["hash"])
        print("Nonce:", block.get("nonce"))
        print("Transactions:")
        for tx in block["transactions"]:
            print("  -", tx)

def pretty_print_pending(pending_file="pending.json"):
    try:
        with open(pending_file, "r") as f:
            pending = json.load(f)
    except:
        pending = []
    if not pending:
        print("No pending transactions.")
        return
    for p in pending:
        print("TXID:", p["txid"], "|", p["sender"], "->", p["receiver"], p["amount"], "fee:", p["fee"])

def show_wallets():
    wallets = load_wallets()
    if not wallets:
        print("No wallets.")
        return
    for k, v in wallets.items():
        print(f"{k}: {v:.2f}")

def main():
    bc = Blockchain()
    while True:
        show_menu()
        choice = input("Choice: ").strip()
        if choice == "1":
            sender = input("Sender (Alice/Bob/Charles): ").strip()
            receiver = input("Receiver: ").strip()
            amt = float(input("Amount: ").strip())
            fee_input = input("Fee (press Enter to use default 2.0): ").strip()
            fee = float(fee_input) if fee_input else 2.0

            tx = Transaction(sender, receiver, amt, fee=fee)
            signed = tx.sign()
            if not signed:
                print("Could not sign transaction — private key missing for sender.")
                continue
            ok, msg = bc.add_transaction(tx)
            print(msg)

        elif choice == "2":
            miner = input("Miner name (wallet must exist or will be created): ").strip()
            ok, msg = bc.mine_block(miner)
            print(msg)

        elif choice == "3":
            pretty_print_chain()

        elif choice == "4":
            valid, msg = bc.is_chain_valid()
            print(msg)

        elif choice == "5":
            show_wallets()

        elif choice == "6":
            pretty_print_pending()

        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

