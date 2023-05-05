from .ZymbitEthKeyring import ZymbitEthKeyring
from .EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
from web3 import Web3
import binascii
import rlp
from typing import Union
from Crypto.Hash import keccak, SHA256
import os
import json

class EthConnect():
    
    @staticmethod
    def create_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1, 
                               max_fee_per_gas: int = 10, gas: int = 21000, to: str = None, 
                               value: int = 0, data: str = "0x", access_list: list = []) -> EthTransaction:

        if not isinstance(chain_id, int) or not isinstance(nonce, int) or not isinstance(max_priority_fee_per_gas, int) \
            or not isinstance(max_fee_per_gas, int) or not isinstance(gas, int) or not isinstance(to, str) \
            or not isinstance(value, int) or not isinstance(data, str) or not isinstance(access_list, list):
            raise ValueError("One or more parameter types are invalid")

        if not Web3.isChecksumAddress(to):
            raise ValueError("'to' field is not a valid checksum address")

        transaction = EthTransaction(
            chain_id = chain_id,
            nonce = nonce,
            max_priority_fee_per_gas = max_priority_fee_per_gas,
            max_fee_per_gas = max_fee_per_gas,
            gas = gas,
            to = binascii.unhexlify(to[2:]),
            value = value,
            data = binascii.unhexlify(data[2:]),
            access_list = access_list
        )

        return transaction
    
    @staticmethod
    def create_deploy_contract_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1,
                                            max_fee_per_gas: int = 10, gas: int = 21000, value: int = 0,
                                            access_list: list = [], contract_bytecode_path: str = None, contract_abi_path: str = None,
                                            constructor_args: list = []) -> EthTransaction:

        if not isinstance(chain_id, int) or not isinstance(nonce, int) or not isinstance(max_priority_fee_per_gas, int) \
                or not isinstance(max_fee_per_gas, int) or not isinstance(gas, int) or not isinstance(value, int) \
                or not isinstance(access_list, list) or not isinstance(contract_bytecode_path, str) or not isinstance(contract_abi_path, str) \
                or not isinstance(constructor_args, list):
            raise ValueError("One or more parameter types are invalid")

        if not os.path.exists(contract_bytecode_path):
            raise ValueError(f"Bytecode file path '{contract_bytecode_path}' does not exist.")

        if not os.path.exists(contract_abi_path):
            raise ValueError(f"ABI file path '{contract_abi_path}' does not exist.")

        with open(contract_bytecode_path, 'r') as bytecode_file:
            bytecode = bytecode_file.read()

        with open(contract_abi_path, 'r') as abi_file:
            abi = json.load(abi_file)

        web3 = Web3()
        contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        data = binascii.unhexlify(contract.constructor(*constructor_args).data_in_transaction[2:])

        transaction = EthTransaction(
            chain_id=chain_id,
            nonce=nonce,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            max_fee_per_gas=max_fee_per_gas,
            gas=gas,
            to=b'',
            value=value,
            data=data,
            access_list=access_list
        )

        return transaction

    @staticmethod
    def create_execute_contract_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1, 
                               max_fee_per_gas: int = 10, gas: int = 210000, contract_address: str = None, 
                               value: int = 0, access_list: list = [], contract_abi_path: str = None, 
                               function_name: str = None, args: list = []) -> EthTransaction:

        if not isinstance(chain_id, int) or not isinstance(nonce, int) or not isinstance(max_priority_fee_per_gas, int) \
            or not isinstance(max_fee_per_gas, int) or not isinstance(gas, int) or not isinstance(contract_address, str) \
            or not isinstance(value, int) or not isinstance(access_list, list) or not isinstance(args, list)\
            or not isinstance(function_name, str) or not isinstance(contract_abi_path, str): 
            raise ValueError("One or more parameter types are invalid")
        
        if not Web3.isChecksumAddress(contract_address):
            raise ValueError("'contract_address' field is not a valid checksum address")
        
        if not os.path.exists(contract_abi_path):
            raise ValueError(f"ABI file path '{contract_abi_path}' does not exist.")

        with open(contract_abi_path, 'r') as f:
            abi = json.load(f)

        web3 = Web3()
        contract = web3.eth.contract(abi=abi, address=contract_address)
        data = contract.encodeABI(fn_name=function_name, args=args)

        transaction = EthTransaction(
            chain_id=chain_id,
            nonce=nonce,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            max_fee_per_gas=max_fee_per_gas,
            gas=gas,
            to=binascii.unhexlify(contract_address[2:]),  # Convert the address to bytes
            value=value,
            data=binascii.unhexlify(data[2:]),  # Convert the data to bytes
            access_list=access_list
        )

        return transaction
    
    @staticmethod
    def sign_transaction(transaction: EthTransaction, keyring: ZymbitEthKeyring, address: str = None, slot: int = None, path: int = None) -> SignedEthTransaction:

        if (not isinstance(transaction, EthTransaction)):
            raise ValueError("Transaction is required to be of type EthTransaction")
        
        if (not isinstance(keyring, ZymbitEthKeyring)):
            raise ValueError("Keyring is required to be of type ZymbitEthKeyring")
        
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        
        return keyring.sign_transaction(transaction, address, slot, path)
    
    @staticmethod
    def rlp_serialize_transaction(transaction: Union[EthTransaction, SignedEthTransaction]) -> bytes:

        if (not (isinstance(transaction, EthTransaction) or isinstance(transaction, SignedEthTransaction))):
            raise ValueError("Transaction has to be of type EthTransaction or SignedEthTransaction")

        encoded_transaction = bytes([transaction.transaction_type]) + rlp.encode(transaction)
        return encoded_transaction

    @staticmethod
    def rlp_deserialize_transaction(encoded_transaction: bytes) -> Union[EthTransaction, SignedEthTransaction]:

        if not isinstance(encoded_transaction, bytes):
            raise ValueError("Encoded transaction must be of type bytes")

        transaction_type = encoded_transaction[0]

        if transaction_type != 2:
            raise ValueError("Only EIP-1559 transactions (type 2) are supported")

        rlp_encoded_transaction = encoded_transaction[1:]

        try:
            transaction = rlp.decode(rlp_encoded_transaction, EthTransaction)
        except rlp.exceptions.DeserializationError:
            try:
                transaction = rlp.decode(rlp_encoded_transaction, SignedEthTransaction)
            except rlp.exceptions.DeserializationError:
                raise ValueError("Failed to deserialize the encoded transaction")

        return transaction
    
    @staticmethod
    def create_message(message: str) -> tuple[str, bytes]:

        if (not isinstance(message, str)):
            raise ValueError("Message must be a string")
        
        eth_prefix = f"Ethereum Signed Message:\n{len(message)}"
        eth_message = eth_prefix + message
        eth_message_bytes = eth_message.encode("utf-8")

        return (eth_message, eth_message_bytes)

    @staticmethod
    def sign_message(message: Union[SHA256.SHA256Hash, keccak.Keccak_Hash], keyring: ZymbitEthKeyring, address: str = None, slot: int = None, path: int = None) -> tuple[int, int, int]:

        if not isinstance(message, (SHA256.SHA256Hash, keccak.Keccak_Hash)):
            raise TypeError("The message must be an instance of either SHA256.SHA256Hash or keccak.Keccak_Hash Crypto.Hash object.")

        if (not ZymbitEthKeyring.is_valid_hash(ZymbitEthKeyring.digest_to_hex(message))):
            raise ValueError("Message is required to be a valid 256 bit digest in hex format")
        
        if (not isinstance(keyring, ZymbitEthKeyring)):
            raise ValueError("Keyring is required to be of type ZymbitEthKeyring")
        
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        
        return keyring.sign_message(message, address, slot, path)
    
    @staticmethod
    def concatenate_sig(v: int, r: int, s: int) -> str:
        if not (v in (27, 28) or (v >= 35 and v % 2 == 1)):
            raise ValueError("Invalid v value.")
        
        N = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        if r < 1 or r >= N:
            raise ValueError("Invalid r value. Must be between 1 and N - 1.")
        
        if s < 1 or s >= N:
            raise ValueError("Invalid s value. Must be between 1 and N - 1.")

        return "0x" + hex(r)[2:].zfill(64) + hex(s)[2:].zfill(64) + hex(v)[2:]
        
    
    @staticmethod
    def keccak256(str_data: str = None, bytes_data: bytes = None) -> keccak.Keccak_Hash:

        if str_data is not None and bytes_data is not None:
            raise ValueError("Both str_data and bytes_data should not be provided at the same time.")
        
        if str_data is None and bytes_data is None:
            raise ValueError("Either str_data or bytes_data should be provided.")

        if str_data is not None:
            data = str_data.encode('utf-8')
        else:
            data = bytes_data

        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(data)
        return keccak_hash
    
    @staticmethod
    def sha256(str_data: str = None, bytes_data: bytes = None) -> SHA256.SHA256Hash:
        if str_data is not None and bytes_data is not None:
            raise ValueError("Both str_data and bytes_data should not be provided at the same time.")

        if str_data is None and bytes_data is None:
            raise ValueError("Either str_data or bytes_data should be provided.")

        if str_data is not None:
            data = str_data.encode('utf-8')
        else:
            data = bytes_data

        sha256_hash = SHA256.new()
        sha256_hash.update(data)

        return sha256_hash
    

    @staticmethod
    def eth_to_wei(ether_amount: float = 0) -> int:
        return Web3.toWei(number = ether_amount, unit = "ether")