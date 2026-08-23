import os
import time
import random
import json
from web3 import Web3

# Load Seed Private Key
seed_key = os.environ.get("EVM_PRIVATE_KEY")
if not seed_key:
    print("ERROR: Missing EVM_PRIVATE_KEY secret.")
    exit()

RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Failed to connect to Sepolia.")
    exit()

account = w3.eth.account.from_key(seed_key)
print(f"=== STATIC DEVELOPER MATRIX STARTED ===")
print(f"Seed Wallet: {account.address}")
print(f"Seed Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} SEPETH")

WALLET_FILE = "wallets.json"

# 1. Load or Generate 50 Wallets
if os.path.exists(WALLET_FILE):
    print("\nLoading existing static wallets...")
    with open(WALLET_FILE, 'r') as f:
        wallets = json.load(f)
    print(f"Loaded {len(wallets)} existing wallets.")
else:
    print("\nGenerating 50 NEW static wallets. (Saving to wallets.json)...")
    wallets = []
    for i in range(50):
        new_acct = w3.eth.account.create()
        wallets.append({
            "address": new_acct.address,
            "key": new_acct.key.hex()
        })
    with open(WALLET_FILE, 'w') as f:
        json.dump(wallets, f, indent=4)
    print("SAVED. These wallets will be reused forever.")

# 2. Fund Empty Wallets (Only costs gas if the wallet is empty)
print("\n=== Checking Wallet Balances & Funding Empty Ones ===")
amount_per_wallet = w3.to_wei(0.002, 'ether') 
gas_price = w3.eth.gas_price
nonce = w3.eth.get_transaction_count(account.address)

for i, wallet in enumerate(wallets):
    balance = w3.eth.get_balance(wallet['address'])
    if balance == 0: # Only fund if empty
        try:
            tx = {
                'nonce': nonce,
                'to': wallet['address'],
                'value': amount_per_wallet,
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': 11155111
            }
            signed = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"Funded Wallet {i+1}. Hash: {tx_hash.hex()[:20]}...")
            nonce += 1
            time.sleep(2)
        except Exception as e:
            print(f"Error funding wallet {i+1}: {e}")
            break
    else:
        print(f"Wallet {i+1} already has balance. Skipping funding.")

print("\nWaiting 30 seconds for funding transactions to confirm...")
time.sleep(30)

# 3. Start the Anti-Sybil DApp Transaction Web
print("\n=== Starting Elite Developer Transaction Web ===")
ERC20_TRANSFER_DATA = bytes.fromhex("a9059cbb000000000000000000000000") + os.urandom(12) + os.urandom(32)

for i, wallet in enumerate(wallets):
    sender = w3.eth.account.from_key(wallet['key'])
    receiver = wallets[(i + 1) % len(wallets)]['address']
    
    balance = w3.eth.get_balance(sender.address)
    if balance > w3.to_wei(0.0001, 'ether'):
        try:
            random_wei = random.randint(100000000000000, 500000000000000)
            
            tx = {
                'nonce': w3.eth.get_transaction_count(sender.address),
                'to': receiver,
                'value': random_wei,
                'gas': 28000, 
                'gasPrice': w3.eth.gas_price,
                'chainId': 11155111,
                'data': ERC20_TRANSFER_DATA
            }
            signed = sender.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"Tx {i+1}/50: Wallet {i+1} -> Wallet {(i % 50) + 2}. Hash: {tx_hash.hex()[:20]}...")
            time.sleep(random.uniform(1, 5))
        except Exception as e:
            print(f"Tx {i+1} failed: {e}")
    else:
        print(f"Wallet {i+1} has no balance. Skipping.")

print("\n=== Static Matrix Run Complete ===")
