import sys
from web3 import Web3
import binascii
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
from ZymbitKeyringManager import ZymbitKeyringManager
from EthConnect import EthConnect
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

ethconnect = EthConnect()

transaction = EthConnect.create_eth_transaction(chain_id=11155111, to=keyring.get_accounts()[0].address, value=EthConnect.eth_to_wei(0.00001))

signedTx = EthConnect.sign_eth_transaction(transaction, keyring1, slot = 30)

serialized = EthConnect.rlp_serialize_transaction(transaction= signedTx)

print(serialized)

deserialized = EthConnect.rlp_deserialize_transaction(serialized)

print(deserialized)

transaction_result_hash = w3.eth.send_raw_transaction(serialized)
print("Transaction broadcast hash:\n%s" %
binascii.hexlify(transaction_result_hash).decode("utf-8"))
