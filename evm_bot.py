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
print(f"=== EVM Sepolia Test Bot Started ===")
print(f"Seed Wallet: {account.address}")
print(f"Seed Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} SEPETH")

# 1. Generate 1 New Wallet
print("\nGenerating 1 new EVM wallet...")
new_acct = w3.eth.account.create()
print(f"New Wallet: {new_acct.address}")

# 2. Send 0.002 ETH to New Wallet
print("\n=== Funding New Wallet ===")
try:
    tx = {
        'nonce': w3.eth.get_transaction_count(account.address),
        'to': new_acct.address,
        'value': w3.to_wei(0.002, 'ether'),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111 # Sepolia
    }
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Funded New Wallet. Hash: {tx_hash.hex()[:20]}...")
except Exception as e:
    print(f"Error funding wallet: {e}")
    exit()

print("\nWaiting 20 seconds for funding to confirm...")
time.sleep(20)

# 3. Start Transaction Web (Send back and forth 2 times)
print("\n=== Starting EVM Transaction Web ===")
for i in range(2):
    # New Wallet sends back to Seed Wallet
    balance = w3.eth.get_balance(new_acct.address)
    if balance > w3.to_wei(0.0001, 'ether'):
        try:
            tx = {
                'nonce': w3.eth.get_transaction_count(new_acct.address),
                'to': account.address,
                'value': w3.to_wei(0.001, 'ether'),
                'gas': 21000,
                'gasPrice': w3.eth.gas_price,
                'chainId': 11155111
            }
            signed = new_acct.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"Tx {i+1}/2: New Wallet -> Seed Wallet. Hash: {tx_hash.hex()[:20]}...")
            time.sleep(15) # Wait for Sepolia block time
        except Exception as e:
            print(f"Tx {i+1} failed: {e}")
            break

print("\n=== EVM Test Run Complete ===")
