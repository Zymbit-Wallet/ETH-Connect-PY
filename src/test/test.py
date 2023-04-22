import sys
from web3 import Web3
import binascii
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
from ZymbitKeyringManager import ZymbitKeyringManager
from EthConnect import EthConnect
from eth_account.messages import encode_defunct
from eth_account import Account
import zymkey


options = {
    "wallet_name": "MyExampleWallet"
}
keyring = ZymbitEthKeyring(options)
options = {
    "wallet_name": "MyExampleWallet1"
}
keyring1 = ZymbitEthKeyring(options)
keyringManager = ZymbitKeyringManager([keyring, keyring1])
print(keyringManager.get_keyrings())

transaction = EthConnect.create_eth_transaction(chain_id=11155111, nonce=2, to=keyring.get_accounts()[1].address, value=EthConnect.eth_to_wei(0.00001))

signedTx = EthConnect.sign_eth_transaction(transaction, keyring1, slot = 30)

serialized = EthConnect.rlp_serialize_transaction(transaction= signedTx)

print(serialized)

deserialized = EthConnect.rlp_deserialize_transaction(serialized)

print(deserialized)

message = EthConnect.create_eth_message('shiv')[0]
sig = EthConnect.sign_message(EthConnect.keccak256(message), keyring, '0x93D458d6B14A02943A07708a24D8A9F142Fc5A00')
concat = EthConnect.concatenate_eth_sig(sig[0], sig[1], sig[2])
print(message)
print(concat)


# transaction_result_hash = w3.eth.send_raw_transaction(serialized)
# print("Transaction broadcast hash:\n%s" %
# binascii.hexlify(transaction_result_hash).decode("utf-8"))
