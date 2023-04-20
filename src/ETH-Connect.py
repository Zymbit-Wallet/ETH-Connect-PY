from ZymbitEthKeyring import ZymbitEthKeyring
from EthAccount import EthAccount
from EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
from web3 import Web3
import binascii

class EthConnect():
    
    def create_eth_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1, max_fee_per_gas: int = 10,
                            gas: int = 21000, to: str = None, value: int = 0, 
                            data: str = "0x", access_list: list = []) -> EthTransaction:

        if (not Web3.isChecksumAddress(to)):
            raise ValueError("To field is not a valid checksum address")

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

    def createContractInvokation():
        pass

    def signMessage():
        pass