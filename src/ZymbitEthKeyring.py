from ZymbitKeyringInterface import ZymbitKeyringInterface
import zymkey

class ZymbitEthKeyring(ZymbitKeyringInterface):
    type: str = "ETH"

    def __init__(self, options: dict = {}) -> None:
        super().__init__(options)

    def serialize(self) -> dict:
        serializedKeyring = {
            "walletName": self.walletName,
            "masterSlot": self.masterSlot
        }
        return serializedKeyring
    
    def deserialize(self, options: dict = {}) -> bool:
        
        return True

    