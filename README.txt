Multi-file Blockchain project (educational prototype)

Requirements:
 - Python 3.8+
 - No extra pip packages required

Files:
 - utils.py
 - wallet.py
 - transaction.py
 - block.py
 - blockchain.py
 - main.py

How to run:
1. Put all files in one folder (e.g., blockchain_project/)
2. Open terminal/cmd and cd into folder.
3. Run:
   python main.py

Behavior:
 - On first run, wallets.json will be created with Alice, Bob, Charles (1000 each).
 - Transactions must be signed (simulated) and will be added to pending pool.
 - Mining selects up to 5 txs, includes fees into miner reward (block reward + fees).
 - Chain is persisted to chain.json; pending mempool to pending.json; wallets to wallets.json.
