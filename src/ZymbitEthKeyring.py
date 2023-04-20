from Keyring import Keyring
from EthAccount import EthAccount
from EllipticCurve import EllipticCurve
import zymkey
from web3 import Web3

class ZymbitEthKeyring(Keyring):
    TYPE: str = "ETH"
    BASE_PATH: str = "m/44'/60'/0'/0"
    CURVE: EllipticCurve = EllipticCurve.secp256k1

    def __init__(self, options: dict = {}) -> None:
        super().__init__(options)

    def serialize(self) -> dict:
        serialized_keyring = {
            "wallet_name": self.wallet_name,
            "master_slot": self.master_slot,
            "type": ZymbitEthKeyring.TYPE,
            "base_path": ZymbitEthKeyring.BASE_PATH,
            "base_slot": self.base_slot,
            "accounts": [account.serialize() for account in self.accounts]
        }
        return serialized_keyring

    def deserialize(self, options: dict = {}) -> bool:
        if "wallet_name" not in options and "master_slot" not in options:
            raise KeyError("wallet_name and master_slot properties required in options")

        if "wallet_name" in options:
            try:
                self.master_slot: int = zymkey.client.get_wallet_key_slot('m', options["wallet_name"])
                self.wallet_name: str = options["wallet_name"]
            except:
                raise ValueError("Invalid wallet_name")
        else:
            try:
                (path, wallet_name, master_slot) = zymkey.client.get_wallet_node_addr(options["master_slot"])
                if path == "m":
                    self.master_slot: int = options["master_slot"]
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
                    self.accounts.append(EthAccount(path, self._generate_eth_address(slot), slot))
                elif path in ZymbitEthKeyring.BASE_PATH and len(path) > len(deepest_path["path"]):
                    deepest_path = {"path": path, "slot": slot}

        if self.base_slot == 0:
            self.base_slot = self._generate_base_path_key(deepest_path)
            
        return True
    
    def add_account(self, index: int = 0) -> EthAccount:
        if (not isinstance(index, int) or index < 0):
            raise ValueError("Invalid index")

        if (self._account_exists(index)):
            raise ValueError("Account already in keyring")

        slot = zymkey.client.gen_wallet_child_key(self.base_slot, index, False)
        new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(index), self._generate_eth_address(slot), slot)
        self.accounts.append(new_account)
        return new_account

    def add_accounts(self, n: int = 1) -> list[EthAccount]:
        if (not isinstance(n, int) or n < 1):
            raise ValueError("Invalid number of accounts to add")

        new_accounts = []

        for i in range(n):
            new_account_index = self._find_next_account_index()
            slot = zymkey.client.gen_wallet_child_key(self.base_slot, new_account_index, False)
            new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(new_account_index), self._generate_eth_address(slot), slot)
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
            if (self._account_exists(index)):
                raise ValueError("account with index " + str(index) + " already in keyring")

        for index in index_list:
            slot = zymkey.client.gen_wallet_child_key(self.base_slot, index, False)
            new_account = EthAccount(ZymbitEthKeyring.BASE_PATH + "/" + str(index), self._generate_eth_address(slot), slot)
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

    def _generate_base_path_key(self, deepest_path) -> int:
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
        return self._generate_base_path_key({"path": path, "slot": slot})

    def _find_next_account_index(self) -> int:
        next_account_index: int = 0
        for account in self.accounts:
            account_index = int(account.path[len(ZymbitEthKeyring.BASE_PATH + "/"):])
            if (account_index >= next_account_index):
                next_account_index = account_index + 1
        return next_account_index

    def _generate_eth_address(self, slot: int) -> str:
        public_key = zymkey.client.get_public_key(slot)
        keccak_hash = Web3.keccak(bytes(public_key)).hex()
        return Web3.toChecksumAddress(keccak_hash[-40:])

    def _account_exists(self, index: int):
        for account in self.accounts:
            if (account.path == ZymbitEthKeyring.BASE_PATH + "/" + str(index)):
                return True
        return False

    def __repr__(self) -> str:
        accounts = "\n\t\t".join([account.__repr__() for account in self.accounts])
        return f"ZymbitEthKeyring(\n\ttype = {ZymbitEthKeyring.TYPE}\n\tbase_path = {ZymbitEthKeyring.BASE_PATH}\n\twallet_name = {self.wallet_name}\n\tmaster_slot = {self.master_slot}\n\tbase_slot = {self.base_slot}\n\taccounts = [\n\t\t{accounts}\n\t]\n)"
