# block.py
import json
from utils import sha256_hex

class Block:
    def __init__(self, index: int, transactions: list, timestamp: str, previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions  # list of tx dicts
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        # Exclude 'hash' itself from calculation: use a deterministic block content
        block_content = {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        return sha256_hex(json.dumps(block_content, sort_keys=True))

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, d: dict):
        b = cls(d["index"], d["transactions"], d["timestamp"], d["previous_hash"], d.get("nonce", 0))
        b.hash = d.get("hash", b.hash)
        return b
