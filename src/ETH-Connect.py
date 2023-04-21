from ZymbitEthKeyring import ZymbitEthKeyring
from EthAccount import EthAccount
from EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
from web3 import Web3
import binascii
import rlp
from typing import Union

class EthConnect():
    
    def create_eth_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1, max_fee_per_gas: int = 10,
                                gas: int = 21000, to: str = None, value: int = 0, 
                                data: str = "0x", access_list: list = []) -> EthTransaction:

        if not isinstance(chain_id, int) or not isinstance(nonce, int) or not isinstance(max_priority_fee_per_gas, int) \
            or not isinstance(max_fee_per_gas, int) or not isinstance(gas, int) or not isinstance(to, str) \
            or not isinstance(value, int) or not isinstance(data, str) or not isinstance(access_list, list):
            raise ValueError("One or more parameter types are invalid")

        if not Web3.isChecksumAddress(to):
            raise ValueError("'to' field is not a valid checksum address")

        transaction = EthTransaction(
            chainId=chain_id,
            nonce=nonce,
            maxPriorityFeePerGas=max_priority_fee_per_gas,
            maxFeePerGas=max_fee_per_gas,
            gas=gas,
            to=binascii.unhexlify(to[2:]),
            value=value,
            data=binascii.unhexlify(data.replace('0x', '')),
            accessList=access_list
        )

        return transaction
    
    def sign_eth_transaction(transaction: EthTransaction, keyring: ZymbitEthKeyring, address: str = None, slot: int = None, path: int = None) -> SignedEthTransaction:

        if (not isinstance(transaction, EthTransaction)):
            raise ValueError("Transaction is required to be of type EthTransaction")
        
        if (not isinstance(keyring, ZymbitEthKeyring)):
            raise ValueError("Keyring is required to be of type ZymbitEthKeyring")
        
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        
        return keyring.sign_transaction(transaction, address, slot, path)
    
    def rlp_serialize_transaction(self, transaction: Union[EthTransaction, SignedEthTransaction]) -> bytes:

        if (not (isinstance(transaction, EthTransaction) or isinstance(transaction, SignedEthTransaction))):
            raise ValueError("Transaction has to be of type EthTransaction or SignedEthTransaction")

        encoded_transaction = bytes([2]) + rlp.encode(transaction)
        return encoded_transaction
        
        
                