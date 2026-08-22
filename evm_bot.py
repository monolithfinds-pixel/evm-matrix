import os
import time
import random
from web3 import Web3

# Load Seed Private Key
seed_key = os.environ.get("EVM_PRIVATE_KEY")
if not seed_key:
    print("ERROR: Missing EVM_PRIVATE_KEY secret.")
    exit()

# Connect to Ethereum Sepolia
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Failed to connect to Sepolia.")
    exit()

account = w3.eth.account.from_key(seed_key)
print(f"=== EVM GOD SCRIPT: Anti-Sybil Matrix Started ===")
print(f"Seed Wallet: {account.address}")
print(f"Seed Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} SEPETH")

# 1. Generate 50 New Wallets
print("\nGenerating 50 new EVM wallets...")
wallets = []
for i in range(50):
    new_acct = w3.eth.account.create()
    wallets.append({
        "address": new_acct.address,
        "key": new_acct.key.hex()
    })
    print(f"Wallet {i+1}: {new_acct.address}")

# 2. Split the 0.05 ETH among the 50 wallets
print("\n=== Splitting Gas Among 50 Wallets ===")
# Keep 0.005 ETH in seed for fees, split 0.045 ETH -> 0.0009 ETH per wallet
amount_per_wallet = w3.to_wei(0.0009, 'ether') 
gas_price = w3.eth.gas_price
nonce = w3.eth.get_transaction_count(account.address)

for i, wallet in enumerate(wallets):
    try:
        tx = {
            'nonce': nonce,
            'to': wallet['address'],
            'value': amount_per_wallet,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 11155111 # Sepolia Chain ID
        }
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Funded Wallet {i+1}. Hash: {tx_hash.hex()[:20]}...")
        nonce += 1
        time.sleep(2) # Wait for nonce to update
    except Exception as e:
        print(f"Error funding wallet {i+1}: {e}")
        break

print("\nWaiting 30 seconds for funding transactions to confirm...")
time.sleep(30)

# 3. Start the Anti-Sybil DApp Transaction Web
print("\n=== Starting Elite DApp Transaction Web ===")

# The 0xa9059cbb function signature simulates an ERC20 Token Transfer
# This tricks the anti-Sybil AI into thinking the wallet is interacting with smart contracts (Uniswap/Aave)
ERC20_TRANSFER_DATA = bytes.fromhex("a9059cbb000000000000000000000000") + os.urandom(12) + os.urandom(32)

for i, wallet in enumerate(wallets):
    sender = w3.eth.account.from_key(wallet['key'])
    # Send to the next wallet in the circle
    receiver = wallets[(i + 1) % len(wallets)]['address']
    
    balance = w3.eth.get_balance(sender.address)
    if balance > w3.to_wei(0.0001, 'ether'):
        try:
            # Send random amount
            random_wei = random.randint(100000000000000, 500000000000000) # 0.0001 to 0.0005 ETH
            
            # Estimate gas for a contract call (costs a bit more, but looks elite)
            tx = {
                'nonce': w3.eth.get_transaction_count(sender.address),
                'to': receiver,
                'value': random_wei,
                'gas': 28000, # Higher gas limit for "smart contract" interaction
                'gasPrice': w3.eth.gas_price,
                'chainId': 11155111,
                'data': ERC20_TRANSFER_DATA # The Protocol Diversity bypass
            }
            signed = sender.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"Tx {i+1}/50: Wallet {i+1} -> Wallet {(i % 50) + 2}. Hash: {tx_hash.hex()[:20]}...")
            
            # Random delay to look human
            time.sleep(random.uniform(1, 5))
        except Exception as e:
            print(f"Tx {i+1} failed: {e}")
    else:
        print(f"Wallet {i+1} has no balance. Skipping.")

print("\n=== EVM Matrix Run Complete ===")
