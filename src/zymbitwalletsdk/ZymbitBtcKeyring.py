from .Keyring import Keyring
from .BtcAccount import BtcAccount
from .EllipticCurve import EllipticCurve
from .EthTransaction import EthTransaction, SignedEthTransaction
import zymkey
import hashlib
from typing import Union
import base58
import re

class ZymbitBtcKeyring(Keyring):
    TYPE: str = "BTC"
    BASE_PATH: str = "m/44'/0'/0'/0"
    CURVE: EllipticCurve = EllipticCurve.secp256k1

    def __init__(self, wallet_name: str = None, master_slot: int = None, test_net: bool = False) -> None:
        if test_net:
            self.BASE_PATH = "m/44'/1'/0'/0"
        super().__init__(wallet_name=wallet_name, master_slot=master_slot)

    def serialize(self) -> dict:
        serialized_keyring = {
            "wallet_name": self.wallet_name,
            "master_slot": self.master_slot,
            "type": ZymbitBtcKeyring.TYPE,
            "curve": ZymbitBtcKeyring.CURVE.get_curve_type(),
            "base_path": self.BASE_PATH,
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
        self.accounts: list[BtcAccount] = []
        deepest_path: dict = {"path": "m", "slot": self.master_slot}

        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))

        for slot in slots:
            (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(slot)
            if wallet_name == self.wallet_name:
                if path == self.BASE_PATH:
                    self.base_slot = slot
                elif (self.BASE_PATH + "/") in path and master_slot == self.master_slot:
                    self.accounts.append(BtcAccount(path, ZymbitBtcKeyring._generate_btc_address(self.BASE_PATH, slot), slot))
                elif path in self.BASE_PATH and len(path) > len(deepest_path["path"]):
                    deepest_path = {"path": path, "slot": slot}

        if self.base_slot == 0:
            self.base_slot = self._generate_base_path_key(self.BASE_PATH, deepest_path)
            
        return True
    
    def add_account(self, index: int = 0) -> BtcAccount:
        if (not isinstance(index, int) or index < 0):
            raise ValueError("Invalid index")

        if (self.account_exists(index)):
            raise ValueError("Account already in keyring")

        slot = zymkey.client.gen_wallet_child_key(self.base_slot, index, False)
        new_account = BtcAccount(self.BASE_PATH + "/" + str(index), ZymbitBtcKeyring._generate_btc_address(self.BASE_PATH, slot), slot)
        self.accounts.append(new_account)
        return new_account

    def add_accounts(self, n: int = 1) -> list[BtcAccount]:
        if (not isinstance(n, int) or n < 1):
            raise ValueError("Invalid number of accounts to add")

        new_accounts = []

        for i in range(n):
            new_account_index = self.find_next_account_index()
            slot = zymkey.client.gen_wallet_child_key(self.base_slot, new_account_index, False)
            new_account = BtcAccount(self.BASE_PATH + "/" + str(new_account_index), ZymbitBtcKeyring._generate_btc_address(self.BASE_PATH, slot), slot)
            new_accounts.append(new_account)
            self.accounts.append(new_account)

        return new_accounts

    def add_accounts_list(self, index_list: list[int] = []) -> list[BtcAccount]:
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
            new_account = BtcAccount(self.BASE_PATH + "/" + str(index), ZymbitBtcKeyring._generate_btc_address(self.base_slot, slot), slot)
            new_accounts.append(new_account)
            self.accounts.append(new_account)

        return new_accounts

    def get_accounts(self) -> list[BtcAccount]:
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
                return
        
        raise ValueError("Account does not exist in keyring")

    @staticmethod
    def _generate_base_path_key(base_path: str, deepest_path) -> int:
        slot = 0
        if deepest_path["path"] == "m":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 44, True)
        elif deepest_path["path"] == "m/44'":
            if base_path == "m/44'/0'/0'/0":
                slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 0, True)
            else:
                slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 1, True)
        elif deepest_path["path"] == "m/44'/0'" or deepest_path["path"] == "m/44'/1'":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 0, True)
        elif deepest_path["path"] == "m/44'/0'/0'" or deepest_path["path"] == "m/44'/1'/0'":
            slot = zymkey.client.gen_wallet_child_key(deepest_path["slot"], 0, False)
        elif deepest_path["path"] == base_path:
            return deepest_path["slot"]
        (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(slot)
        return ZymbitBtcKeyring._generate_base_path_key(base_path, {"path": path, "slot": slot})

    def find_next_account_index(self) -> int:
        next_account_index: int = 0
        for account in self.accounts:
            account_index = int(account.path[len(self.BASE_PATH + "/"):])
            if (account_index >= next_account_index):
                next_account_index = account_index + 1
        return next_account_index
    
    @staticmethod
    def _generate_btc_address(base_path: str, slot: int) -> str:
        public_key = zymkey.client.get_public_key(slot)

        sha256 = hashlib.sha256()
        sha256.update(public_key)
        sha256_result = sha256.digest()

        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_result)
        ripemd160_result = ripemd160.digest()

        # Add network byte (0x00 for Bitcoin mainnet)
        if base_path == "m/44'/0'/0'/0":
            network_byte = b'\x00'
        else:
            network_byte = b'\x6F'
        network_and_ripemd160 = network_byte + ripemd160_result

        checksum_full = hashlib.sha256(hashlib.sha256(network_and_ripemd160).digest()).digest()
        checksum = checksum_full[:4]

        binary_address = network_and_ripemd160 + checksum
        btc_address = base58.b58encode(binary_address)

        return btc_address.decode('utf-8')

    def account_exists(self, index: int):
        for account in self.accounts:
            if (account.path == self.BASE_PATH + "/" + str(index)):
                return True
        return False

    def __repr__(self) -> str:
        accounts = "\n\t\t".join([account.__repr__() for account in self.accounts])
        return f"ZymbitBtcKeyring(\n\ttype = {ZymbitBtcKeyring.TYPE}\n\tbase_path = {self.BASE_PATH}\n\twallet_name = {self.wallet_name}\n\tmaster_slot = {self.master_slot}\n\tbase_slot = {self.base_slot}\n\taccounts = [\n\t\t{accounts}\n\t]\n)"
