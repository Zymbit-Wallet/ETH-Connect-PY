from Account import Account
import zymkey
import binascii

class EthAccount(Account):
    def __init__(self, path: str, address: str, slot: int) -> None:
        self.path = path
        self.address = address
        self.slot = slot

    def serialize(self) -> dict:
        return {
            "path": self.path,
            "address": self.address,
            "slot": self.slot
        }

    def getPublicKey(self) -> str:
        publicKey = zymkey.client.get_public_key(self.slot)
        return '0x' + binascii.hexlify(publicKey).decode('utf-8')
    
    def __repr__(self) -> str:
        return f"(Path: {self.path}, Address: {self.address}, Slot: {self.slot})"