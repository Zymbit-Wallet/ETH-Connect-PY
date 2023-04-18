from ZymbitKeyringInterface import ZymbitKeyringInterface
import zymkey


class ZymbitEthKeyring(ZymbitKeyringInterface):
    type: str = "ETH"
    path: str = "m/44'/60'/0'/0"

    def __init__(self, options: dict = {}) -> None:
        super().__init__(options)

    def serialize(self) -> dict:
        serializedKeyring = {
            "walletName": self.walletName,
            "masterSlot": self.masterSlot
        }
        return serializedKeyring

    def deserialize(self, options: dict = {}) -> None:
        if ("walletName" not in options and "masterSlot" not in options):
            raise KeyError("walletName and masterSlot properties missing from options")

        if("walletName" in options):
            try:
                self.masterSlot: int = zymkey.client.get_wallet_key_slot('m', options["walletName"])
                self.walletName: str = options["walletName"]
            except:
                raise ValueError("Invalid walletName")
        else:
            try:
                (path, walletName, slotNumber) = zymkey.client.get_wallet_node_addr(options["masterSlot"])
                if (path == "m"):
                    self.masterSlot: int = options["masterSlot"]
                    self.walletName: str = walletName
                else:
                    raise
            except:
                raise ValueError("Invalid masterSlot")

        self.baseSlot: int = 0
        self.accounts: list = []
        deepestPath: dict = {"path": "m", "slot": self.masterSlot}

        slots: list = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))

        for slot in slots:
            (path, walletName, slotNumber) = zymkey.client.get_wallet_node_addr(slot)
            if (walletName == self.walletName):
                if (path == self.path):
                    self.baseSlot = slot
                elif ((self.path + "/") in path):
                    self.accounts.append({"path": path, "slot": slot})
                elif (path in self.path and len(path) > len(deepestPath["path"])):
                    deepestPath = {"path": path, "slot": slot}
        
        if(self.baseSlot == 0):
            self.baseSlot = self._generateBasePathKey(deepestPath)
            
        return

    def _generateBasePathKey(self, deepestPath):
        slot = 0
        if deepestPath["path"] == "m":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 44, True)
        elif deepestPath["path"] == "m/44'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 60, True)
        elif deepestPath["path"] == "m/44'/60'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 0, True)
        elif deepestPath["path"] == "m/44'/60'/0'":
            slot = zymkey.client.gen_wallet_child_key(deepestPath["slot"], 0, False)
        elif deepestPath["path"] == self.path:
            return deepestPath["slot"]
        (path, walletName, slotNumber) = zymkey.client.get_wallet_node_addr(slot)
        return self._generateBasePathKey({"path": path, "slot": slot})
            
