from web3 import Web3
import os, time

INFURA = os.getenv("INFURA_URL")
ADDRESS = os.getenv("WALLET_ADDRESS")
KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(INFURA))

contract_address = "DEPLOYED_CONTRACT"
contract_abi = [{"inputs":[],"name":"loop","outputs":[],"stateMutability":"payable","type":"function"}]

def whisper_loop():
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    nonce = w3.eth.getTransactionCount(ADDRESS)
    tx = contract.functions.loop().build_transaction({
        'from': ADDRESS,
        'value': w3.toWei(0.001, 'ether'),
        'gas': 120000,
        'gasPrice': w3.toWei('30', 'gwei'),
        'nonce': nonce
    })
    signed = w3.eth.account.sign_transaction(tx, KEY)
    sent = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"🔥 Whisper loop triggered: {sent.hex()}")

while True:
    whisper_loop()
    time.sleep(300)  # Every 5 min
