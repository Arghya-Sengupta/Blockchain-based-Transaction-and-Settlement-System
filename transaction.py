# transaction.py
from dataclasses import dataclass, asdict
from utils import now_iso, sha256_hex
from wallet import get_private_key

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    fee: float = 2.0
    timestamp: str = None
    txid: str = None
    signature: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = now_iso()
        if self.txid is None:
            self.txid = self.compute_txid()

    def compute_txid(self) -> str:
        raw = f"{self.sender}|{self.receiver}|{self.amount}|{self.fee}|{self.timestamp}"
        return sha256_hex(raw)

    def to_dict(self):
        return asdict(self)

    # -- Simulated signature using sender's private key --
    def sign(self):
        priv = get_private_key(self.sender)
        if not priv:
            # No local private key available -> cannot sign
            return False
        raw = f"{self.sender}|{self.receiver}|{self.amount}|{self.timestamp}|{priv}"
        self.signature = sha256_hex(raw)
        return True

    def verify_signature(self) -> bool:
        # For "SYSTEM" sender (coinbase/reward), we skip signature verification
        if self.sender == "SYSTEM":
            return True
        if not self.signature:
            return False
        # Recompute expected signature using stored simulated private key
        priv = get_private_key(self.sender)
        if not priv:
            return False
        expected = sha256_hex(f"{self.sender}|{self.receiver}|{self.amount}|{self.timestamp}|{priv}")
        return expected == self.signature
