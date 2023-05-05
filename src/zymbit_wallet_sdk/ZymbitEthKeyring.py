from .Keyring import Keyring
from .EthAccount import EthAccount
from .EllipticCurve import EllipticCurve
from .EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
from web3 import Web3
from Crypto.Hash import keccak, SHA256
from typing import Union
import rlp
import re

class ZymbitEthKeyring(Keyring):
    TYPE: str = "ETH"
    BASE_PATH: str = "m/44'/60'/0'/0"
    CURVE: EllipticCurve = EllipticCurve.secp256k1

    def __init__(self, wallet_name: str = None, master_slot: int = None) -> None:
        super().__init__(wallet_name=wallet_name, master_slot=master_slot)

    def serialize(self) -> dict:
        serialized_keyring = {
            "wallet_name": self.wallet_name,
            "master_slot": self.master_slot,
            "type": ZymbitEthKeyring.TYPE,
            "curve": ZymbitEthKeyring.CURVE.get_curve_type(),
            "base_path": ZymbitEthKeyring.BASE_PATH,
            "base_slot": self.base_slot,
            "accounts": [account.serialize() for account in self.accounts]
        }
        return serialized_keyring

    def deserialize(self, wallet_name: str = None, master_slot: int = None) -> bool:
        if not wallet_name and not master_slot:
            raise ValueError("wallet_name or master_slot required")
        
        if wallet_name and master_slot:
            raise ValueError("Can't provide both wallet_name and master_slot")

        if wallet_name:
            try:
                self.master_slot: int = zymkey.client.get_wallet_key_slot('m', wallet_name)
                self.wallet_name: str = wallet_name
            except:
                raise ValueError("Invalid wallet_name")
        else:
            try:
                (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(master_slot)
                if path == "m":
                    self.master_slot: int = master_slot
                    self.wallet_name: str = wallet_name
                else:
                    raise
            except:
                raise ValueError("Invalid master_slot")

        self.base_slot: int = 0
        self.accounts: list[EthAccount] = []
        deepest_path: dict = {"path": "m", "slot": self.master_slot}

        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))

        for slot in slots:
            (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(slot)
            if wallet_name == self.wallet_name:
                if path == ZymbitEthKeyring.BASE_PATH:
                    self.base_slot = slot
                elif (ZymbitEthKeyring.BASE_PATH + "/") in path and master_slot == self.master_slot:
                    self.accounts.append(EthAccount(path, ZymbitEthKeyring.generate_eth_address(slot), slot))
                elif path in ZymbitEthKeyring.BASE_PATH and len(path) > len(deepest_path["path"]):
                    deepest_path = {"path": path, "slot": slot}

        if self.base_slot == 0:
            self.base_slot = self._generate_base_path_key(deepest_path)
            
        return True
    
    def add_account(self, index: int = 0) -> EthAccount:
        if (not isinstance(index, int) or index < 0):
            raise ValueError("Invalid index")

        if (self.account_exists(index)):
            raise ValueError("Account already in keyring")

        slot = zymkey.client.gen_wallet_child_key(self.base_slot, index, False)
        new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(index), ZymbitEthKeyring.generate_eth_address(slot), slot)
        self.accounts.append(new_account)
        return new_account

    def add_accounts(self, n: int = 1) -> list[EthAccount]:
        if (not isinstance(n, int) or n < 1):
            raise ValueError("Invalid number of accounts to add")

        new_accounts = []

        for i in range(n):
            new_account_index = self._find_next_account_index()
            slot = zymkey.client.gen_wallet_child_key(self.base_slot, new_account_index, False)
            new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(new_account_index), ZymbitEthKeyring.generate_eth_address(slot), slot)
            new_accounts.append(new_account)
            self.accounts.append(new_account)

        return new_accounts

    def add_accounts_list(self, index_list: list[int] = []) -> list[EthAccount]:
        new_accounts = []
        if (not all(isinstance(index, int) and index >= 0 for index in index_list)):
            raise ValueError("Invalid list of indexes")

        if (len(index_list) < 1):
            return new_accounts

        for index in index_list:
            if (self.account_exists(index)):
                raise ValueError("account with index " + str(index) + " already in keyring")

        for index in index_list:
            slot = zymkey.client.gen_wallet_child_key(self.base_slot, index, False)
            new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(index), ZymbitEthKeyring.generate_eth_address(slot), slot)
            new_accounts.append(new_account)
            self.accounts.append(new_account)

        return new_accounts

    def get_accounts(self) -> list[EthAccount]:
        return self.accounts

    def remove_account(self, address: str = None, slot: int = None, path: int = None) -> bool:
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                zymkey.client.remove_key(account.slot)
                self.accounts.remove(account)
                return True
        return False

    def get_public_key(self, address: str = None, slot: int = None, path: int = None) -> str:
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                return account.get_public_key()
        return ValueError("Account not in keyring")
    
    def sign_transaction(self, transaction: EthTransaction, address: str = None, slot: int = None, path: int = None):

        if (not isinstance(transaction, EthTransaction)):
            raise ValueError("Transaction is required to be of type EthTransaction")

        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")
        
        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                encoded_transaction = bytes([transaction.transaction_type]) + rlp.encode(transaction)
                keccak_digest = keccak.new(digest_bits=256)
                keccak_digest.update(encoded_transaction)
                (signature, raw_y_parity) = zymkey.client.sign_digest(keccak_digest, account.slot, return_recid=True)
                (y_parity, v, r, s) = self.gen_valid_eth_sig(signature, raw_y_parity, transaction.chain_id)
                signedTransaction = SignedEthTransaction(
                    chain_id = transaction.chain_id,
                    nonce = transaction.nonce,
                    max_priority_fee_per_gas = transaction.max_priority_fee_per_gas,
                    max_fee_per_gas = transaction.max_fee_per_gas,
                    gas = transaction.gas,
                    to = transaction.to,
                    value = transaction.value,
                    data = transaction.data,
                    access_list = transaction.access_list,
                    y_parity = y_parity,
                    r = r,
                    s = s
                )
                return signedTransaction
        
        raise ValueError("Account does not exist in keyring")
    
    def sign_message(self, message: Union[SHA256.SHA256Hash, keccak.Keccak_Hash], address: str = None, slot: int = None, path: int = None) -> tuple[int, int, int]:

        if not isinstance(message, (SHA256.SHA256Hash, keccak.Keccak_Hash)):
            raise TypeError("The message must be an instance of either SHA256.SHA256Hash or keccak.Keccak_Hash Crypto.Hash object.")

        if (not ZymbitEthKeyring.is_valid_hash(ZymbitEthKeyring.digest_to_hex(message))):
            raise ValueError("Message is required to be a valid 256 bit digest in hex format")
        
        if (not (slot or address or path)):
            raise ValueError("Valid address, slot, or path required")

        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                (signature, raw_y_parity) = zymkey.client.sign_digest(message, account.slot, return_recid=True)
                (y_parity, v, r, s) = ZymbitEthKeyring.gen_valid_eth_sig(signature, raw_y_parity)
                return (v, r, s)
            
        raise ValueError("Account does not exist in keyring") 

    @staticmethod
    def _generate_base_path_key(deepest_path) -> int:
        slot = 0
        if deepest_path["path"] == "m":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 44, True)
        elif deepest_path["path"] == "m/44'":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 60, True)
        elif deepest_path["path"] == "m/44'/60'":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 0, True)
        elif deepest_path["path"] == "m/44'/60'/0'":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 0, False)
        elif deepest_path["path"] == ZymbitEthKeyring.BASE_PATH:
            return deepest_path["slot"]
        (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(slot)
        return ZymbitEthKeyring._generate_base_path_key({"path": path, "slot": slot})

    def _find_next_account_index(self) -> int:
        next_account_index: int = 0
        for account in self.accounts:
            account_index = int(account.path[len(ZymbitEthKeyring.BASE_PATH + "/"):])
            if (account_index >= next_account_index):
                next_account_index = account_index + 1
        return next_account_index
    
    @staticmethod
    def generate_eth_address(slot: int) -> str:
        public_key = zymkey.client.get_public_key(slot)
        keccak_hash = Web3.keccak(bytes(public_key)).hex()
        return Web3.toChecksumAddress(keccak_hash[-40:])

    def account_exists(self, index: int):
        for account in self.accounts:
            if (account.path == ZymbitEthKeyring.BASE_PATH + "/" + str(index)):
                return True
        return False
    
    @staticmethod
    def digest_to_hex(digest: Union[SHA256.SHA256Hash, keccak.Keccak_Hash]) -> str:

        if not isinstance(digest, (SHA256.SHA256Hash, keccak.Keccak_Hash)):
            raise TypeError("The digest must be an instance of either SHA256.SHA256Hash or keccak.Keccak_Hash Crypto.Hash object.")
        
        return "0x" + digest.hexdigest()
    
    @staticmethod
    def gen_valid_eth_sig(signature: bytearray, y_parity: int, chain_id: int = 0) -> tuple[bool, int, int, int]:
            N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
            r = int.from_bytes(signature[:32], "big")
            s = int.from_bytes(signature[-32:], "big")

            y_parity = bool(y_parity.value)
            if((s*2) >= N):
                y_parity = not y_parity
                s = N - s

            if (chain_id):
                v = 35 + (chain_id * 2) + (1 if y_parity else 0)
            else:
                v = 27 + (1 if y_parity else 0)

            return (y_parity, v, r, s)
    
    @staticmethod
    def is_valid_hash(hex_hash: str) -> bool:
        if re.match("^(0x)?[0-9a-fA-F]{64}$", hex_hash):
            return True
        return False

    def __repr__(self) -> str:
        accounts = "\n\t\t".join([account.__repr__() for account in self.accounts])
        return f"ZymbitEthKeyring(\n\ttype = {ZymbitEthKeyring.TYPE}\n\tbase_path = {ZymbitEthKeyring.BASE_PATH}\n\twallet_name = {self.wallet_name}\n\tmaster_slot = {self.master_slot}\n\tbase_slot = {self.base_slot}\n\taccounts = [\n\t\t{accounts}\n\t]\n)"
