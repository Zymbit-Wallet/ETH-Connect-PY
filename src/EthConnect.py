from ZymbitEthKeyring import ZymbitEthKeyring
from EthAccount import EthAccount
from EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
from web3 import Web3
import binascii
import rlp
from typing import Union
from Crypto.Hash import keccak, SHA256
import hashlib

class EthConnect():
    
    @staticmethod
    def create_eth_transaction(chain_id: int = 1, nonce: int = 0, max_priority_fee_per_gas: int = 1, 
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
            data = binascii.unhexlify(data.replace('0x', '')),
            access_list = access_list
        )

        return transaction
    
    @staticmethod
    def sign_eth_transaction(transaction: EthTransaction, keyring: ZymbitEthKeyring, address: str = None, slot: int = None, path: int = None) -> SignedEthTransaction:

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

        encoded_transaction = bytes([2]) + rlp.encode(transaction)
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

    def sign_message(message: Union[SHA256.SHA256Hash, keccak.Keccak_Hash], keyring: ZymbitEthKeyring, address: str = None, slot: int = None, path: int = None) -> tuple[int, int, int]:

        if not isinstance(message, (SHA256.SHA256Hash, keccak.Keccak_Hash)):
            raise TypeError("The message must be an instance of either SHA256.SHA256Hash or keccak.Keccak_Hash Crypto.Hash object.")

        if (not ZymbitEthKeyring._is_valid_hash(ZymbitEthKeyring._digest_to_hex(message))):
            raise ValueError("Message is required to be a valid 256 bit digest in hex format")
        
        if (not isinstance(keyring, ZymbitEthKeyring)):
            raise ValueError("Keyring is required to be of type ZymbitEthKeyring")
        
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        
        return keyring.sign_message(message, address, slot, path)
    
    @staticmethod
    def concatenate_eth_sig(v: int, r: int, s: int) -> str:
        if not (v in (27, 28) or (v >= 35 and v % 2 == 1)):
            raise ValueError("Invalid v value.")
        
        N = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        if r < 1 or r >= N:
            raise ValueError("Invalid r value. Must be between 1 and N - 1.")
        
        if s < 1 or s >= N:
            raise ValueError("Invalid s value. Must be between 1 and N - 1.")

        v_bytes = v.to_bytes(1, byteorder='big')
        r_bytes = r.to_bytes(32, byteorder='big')
        s_bytes = s.to_bytes(32, byteorder='big')

        concatenated_sig = v_bytes + r_bytes + s_bytes
        return "0x" + concatenated_sig.hex()
        
    
    @staticmethod
    def keccak256(str_data: str = None, bytes_data: bytes = None) -> str:

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
    def sha256(str_data: str = None, bytes_data: bytes = None) -> str:
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