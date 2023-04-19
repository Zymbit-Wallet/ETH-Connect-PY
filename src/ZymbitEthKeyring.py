from Keyring import Keyring
from EthAccount import EthAccount
from EllipticCurve import EllipticCurve
import zymkey
from web3 import Web3

class ZymbitEthKeyring(Keyring):
    TYPE: str = "ETH"
    BASEPATH: str = "m/44'/60'/0'/0"
    CURVE: EllipticCurve = EllipticCurve.secp256k1

    def __init__(self, options: dict = {}) -> None:
        super().__init__(options)

    def serialize(self) -> dict:
        serializedKeyring = {
            "walletName": self.walletName,
            "masterSlot": self.masterSlot,
            "type": ZymbitEthKeyring.TYPE,
            "basePath": ZymbitEthKeyring.BASEPATH,
            "baseSlot": self.baseSlot,
            "accounts": [account.serialize() for account in self.accounts]
        }
        return serializedKeyring

    def deserialize(self, options: dict = {}) -> None:
        if ("walletName" not in options and "masterSlot" not in options):
            raise KeyError("walletName and masterSlot properties missing from options")

        if ("walletName" in options):
            try:
                self.masterSlot: int = zymkey.client.get_wallet_key_slot('m', options["walletName"])
                self.walletName: str = options["walletName"]
            except:
                raise ValueError("Invalid walletName")
        else:
            try:
                (path, walletName, masterSlot) = zymkey.client.get_wallet_node_addr(options["masterSlot"])
                if (path == "m"):
                    self.masterSlot: int = options["masterSlot"]
                    self.walletName: str = walletName
                else:
                    raise
            except:
                raise ValueError("Invalid masterSlot")

        self.baseSlot: int = 0
        self.accounts: list[EthAccount] = []
        deepestPath: dict = {"path": "m", "slot": self.masterSlot}

        slots: list = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))

        for slot in slots:
            (path, walletName, masterSlot) = zymkey.client.get_wallet_node_addr(slot)
            if (walletName == self.walletName):
                if (path == ZymbitEthKeyring.BASEPATH):
                    self.baseSlot = slot
                elif ((ZymbitEthKeyring.BASEPATH + "/") in path and masterSlot == self.masterSlot):
                    self.accounts.append(EthAccount(path, self._generateEthAddress(slot), slot))
                elif (path in ZymbitEthKeyring.BASEPATH and len(path) > len(deepestPath["path"])):
                    deepestPath = {"path": path, "slot": slot}

        if (self.baseSlot == 0):
            self.baseSlot = self._generateBasePathKey(deepestPath)
            
        return

    def addAccount(self, index: int = 0) -> EthAccount:
        if (not isinstance(index, int) or index < 0):
            raise ValueError("Invalid index")

        if (self._accountExists(index)):
            raise ValueError("Account already in keyring")
        
        slot = zymkey.client.gen_wallet_child_key(self.baseSlot, index, False)
        newAccount = EthAccount(ZymbitEthKeyring.BASEPATH + "/" + str(index), self._generateEthAddress(slot), slot)
        self.accounts.append(newAccount)
        return newAccount

    def addAccounts(self, n: int = 1) -> list[EthAccount]:
        if (not isinstance(n, int) or n < 1):
            raise ValueError("Invalid number of accounts to add")

        newAccounts = []
        
        for i in range(n):
            newAccountIndex = self._findNextAccountIndex()
            slot = zymkey.client.gen_wallet_child_key(self.baseSlot, newAccountIndex, False)
            newAccount = EthAccount(ZymbitEthKeyring.BASEPATH + "/" + str(newAccountIndex), self._generateEthAddress(slot), slot)
            newAccounts.append(newAccount)
            self.accounts.append(newAccount)
        
        return newAccounts
    
    def addAccountsList(self, indexList: list[int] = []) -> list[EthAccount]:
        newAccounts = []
        if (not all(isinstance(index, int) and index >= 0 for index in indexList)):
            raise ValueError("Invalid list of indexes")
        
        if (len(indexList) < 1):
            return newAccounts
        
        for index in indexList:
            if (self._accountExists(index)):
                raise ValueError("account with index " + str(index) + " already in keyring")
        
        for index in indexList:
            slot = zymkey.client.gen_wallet_child_key(self.baseSlot, index, False)
            newAccount = EthAccount(ZymbitEthKeyring.BASEPATH + "/" + str(index), self._generateEthAddress(slot), slot)
            newAccounts.append(newAccount)
            self.accounts.append(newAccount)
        
        return newAccounts
    
    def getAccounts(self) -> list[EthAccount]:
        return self.accounts

    def removeAccount(self, address: str = None, slot: int = None, path: int = None) -> bool:
        if (slot is None and address is None and path is None):
            raise ValueError("Valid address, slot, or path required")
        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                zymkey.client.remove_key(account.slot)
                self.accounts.remove(account)
                return True
        return False
    
    def getPublicKey(self, address: str = None, slot: int = None, path: int = None) -> str:
        if (slot is None and address is None and path is None):
            raise ValueError("Valid address, slot, or path required")
        for account in self.accounts:
            if (account.address == address or account.slot == slot or account.path == path):
                return account.getPublicKey()
        return ValueError("Account not in keyring")

    def _generateBasePathKey(self, deepestPath) -> int:
        slot = 0
        if deepestPath["path"] == "m":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 44, True)
        elif deepestPath["path"] == "m/44'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 60, True)
        elif deepestPath["path"] == "m/44'/60'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 0, True)
        elif deepestPath["path"] == "m/44'/60'/0'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 0, False)
        elif deepestPath["path"] == ZymbitEthKeyring.BASEPATH:
            return deepestPath["slot"]
        (path, walletName, masterSlot) = zymkey.client.get_wallet_node_addr(slot)
        return self._generateBasePathKey({"path": path, "slot": slot})
    
    def _findNextAccountIndex(self) -> int:
        nextAccountIndex: int = 0
        for account in self.accounts:
            accountIndex = int(account.path[len(ZymbitEthKeyring.BASEPATH + "/"):])
            if (accountIndex >= nextAccountIndex):
                nextAccountIndex = accountIndex + 1
        return nextAccountIndex
    
    def _generateEthAddress(self, slot: int) -> str:
        publicKey = zymkey.client.get_public_key(slot)
        keccakHash = Web3.keccak(bytes(publicKey)).hex()
        return Web3.toChecksumAddress(keccakHash[-40:])

    def _accountExists(self, index: int):
        for account in self.accounts:
            if (account.path == ZymbitEthKeyring.BASEPATH + "/" + str(index)):
                return True
        return False
    
    def __repr__(self) -> str:
        accounts = "\n\t\t".join([account.__repr__() for account in self.accounts])
        return f"ZymbitEthKeyring(\n\ttype = {ZymbitEthKeyring.TYPE}\n\tbasePath = {ZymbitEthKeyring.BASEPATH}\n\twalletName = {self.walletName}\n\tmasterSlot = {self.masterSlot}\n\tbaseSlot = {self.baseSlot}\n\taccounts = [\n\t\t{accounts}\n\t]\n)"
