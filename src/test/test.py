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

transaction = EthConnect.create_transaction(chain_id=11155111, nonce=2, to=keyring.get_accounts()[1].address, value=EthConnect.eth_to_wei(0.00001))

signedTx = EthConnect.sign_transaction(transaction, keyring1, slot = 30)

serialized = EthConnect.rlp_serialize_transaction(transaction= signedTx)


deserialized = EthConnect.rlp_deserialize_transaction(serialized)


message = EthConnect.create_message('shiv')
sig = EthConnect.sign_message(EthConnect.keccak256(message[0]), keyring, '0x93D458d6B14A02943A07708a24D8A9F142Fc5A00')
concat = EthConnect.concatenate_sig(sig[0], sig[1], sig[2])
print(message)
print(concat)

contractTxn = EthConnect.create_execute_contract_transaction(chain_id=11155111, nonce=4, contract_abi_path='./ABI.json', args=['hi','hi1', 1000000, '0x'+('0'*64), '0x' + ('0'*130)], function_name="postData", contract_address = '0x6FCc62196FD8C0f1a92817312c109D438cC0acC9')
print(contractTxn)

signedContractTxn = EthConnect.sign_transaction(contractTxn, keyring1, slot=30)

print(signedContractTxn)

serialized = EthConnect.rlp_serialize_transaction(transaction= signedContractTxn)


deserialized = EthConnect.rlp_deserialize_transaction(serialized)



transaction_result_hash = w3.eth.send_raw_transaction(serialized)
print("Transaction broadcast hash:\n%s" %
binascii.hexlify(transaction_result_hash).decode("utf-8"))
