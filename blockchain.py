# blockchain.py
import json
import os
from typing import List
from utils import now_iso, sha256_hex
from block import Block
from transaction import Transaction
from wallet import initialize_default_wallets, credit_wallet, debit_wallet, get_balance

CHAIN_FILE = "chain.json"
PENDING_FILE = "pending.json"

BLOCK_REWARD = 5.0
TX_FEE_DEFAULT = 2.0
MAX_TX_PER_BLOCK = 5

class Blockchain:
    def __init__(self):
        initialize_default_wallets()
        self.chain: List[dict] = self.load_chain()
        self.pending: List[dict] = self.load_pending()
        if len(self.chain) == 0:
            self.create_genesis()

    # ---------- Persistence ----------
    def load_chain(self):
        if not os.path.exists(CHAIN_FILE):
            return []
        with open(CHAIN_FILE, "r") as f:
            return json.load(f)

    def save_chain(self):
        with open(CHAIN_FILE, "w") as f:
            json.dump(self.chain, f, indent=2)

    def load_pending(self):
        if not os.path.exists(PENDING_FILE):
            return []
        with open(PENDING_FILE, "r") as f:
            return json.load(f)

    def save_pending(self):
        with open(PENDING_FILE, "w") as f:
            json.dump(self.pending, f, indent=2)

    # ---------- Genesis ----------
    def create_genesis(self):
        genesis = Block(0, [], now_iso(), "0")
        self.chain.append(genesis.to_dict())
        self.save_chain()

    # ---------- Difficulty (auto-adjust every 3 blocks) ----------
    def current_difficulty(self) -> int:
        blocks = len(self.chain)
        return max(2, 2 + (blocks // 3))

    # ---------- Utility ----------
    def last_block(self) -> dict:
        return self.chain[-1]

    # ---------- Add transaction ----------
    def add_transaction(self, tx: Transaction) -> (bool, str):
        # verify signature
        if not tx.verify_signature():
            return False, "Invalid signature."

        # check sender balance considering pending outgoing transactions
        sender = tx.sender
        needed = tx.amount + tx.fee

        confirmed_balance = get_balance(sender)
        pending_outgoing = sum(p["amount"] + p["fee"] for p in self.pending if p["sender"] == sender)

        if confirmed_balance - pending_outgoing < needed:
            return False, f"Insufficient funds. Available (confirmed - pending_outgoing) = {confirmed_balance - pending_outgoing:.2f}"

        # debit sender immediately to prevent double spend
        debit_wallet(sender, needed)

        # add to pending (mempool)
        self.pending.append(tx.to_dict())
        self.save_pending()
        return True, f"Transaction {tx.txid} added to mempool."

    # ---------- Select transactions for next block ----------
    def select_transactions_for_block(self):
        sorted_pool = sorted(self.pending, key=lambda p: (-p.get("fee", TX_FEE_DEFAULT), p.get("timestamp")))
        selection = sorted_pool[:MAX_TX_PER_BLOCK]
        return selection

    # ---------- Mine a block ----------
    def mine_block(self, miner_name: str) -> (bool, str):
        if not self.pending:
            return False, "No transactions to mine."

        selected = self.select_transactions_for_block()

        # compute total fees
        total_fees = sum(p.get("fee", TX_FEE_DEFAULT) for p in selected)
        miner_reward = BLOCK_REWARD + total_fees

        # Create reward tx (SYSTEM -> miner), fee=0
        reward_tx = Transaction("SYSTEM", miner_name, miner_reward, fee=0.0)

        # Credit receiver wallets here (on block confirmation)
        for tx in selected:
            credit_wallet(tx["receiver"], tx["amount"])

        block_txs = selected + [reward_tx.to_dict()]

        last = self.last_block()
        new_index = last["index"] + 1
        new_block = Block(new_index, block_txs, now_iso(), last["hash"])

        # Proof-of-work
        difficulty = self.current_difficulty()
        prefix = "0" * difficulty
        while not new_block.hash.startswith(prefix):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        # Append block
        self.chain.append(new_block.to_dict())
        self.save_chain()

        # Remove selected txs from pending
        selected_txids = set(p["txid"] for p in selected)
        self.pending = [p for p in self.pending if p["txid"] not in selected_txids]
        self.save_pending()

        # credit miner wallet
        credit_wallet(miner_name, miner_reward)

        return True, f"Block {new_index} mined. Miner reward: {miner_reward:.2f} (includes fees). Difficulty was {difficulty}"

    # ---------- Chain validation ----------
    def is_chain_valid(self) -> (bool, str):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr["previous_hash"] != prev["hash"]:
                return False, f"Broken link at index {i}"
            temp = curr.copy()
            stored_hash = temp.pop("hash")
            recalculated = sha256_hex(json.dumps({
                "index": temp["index"],
                "transactions": temp["transactions"],
                "timestamp": temp["timestamp"],
                "previous_hash": temp["previous_hash"],
                "nonce": temp.get("nonce", 0)
            }, sort_keys=True))
            if recalculated != stored_hash:
                return False, f"Invalid hash at index {i}"
        return True, "Chain valid."
