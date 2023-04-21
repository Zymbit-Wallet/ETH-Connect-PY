import sys
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

transaction = EthConnect.create_eth_transaction(to=keyring.get_accounts()[0].address)

signedTx = EthConnect.sign_eth_transaction(transaction, keyring, path = "m/44'/60'/0'/0/2")

serialized = EthConnect.rlp_serialize_transaction(transaction= signedTx)

deserialized = EthConnect.rlp_deserialize_transaction(serialized)

print(deserialized)