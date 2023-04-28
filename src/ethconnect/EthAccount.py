from .Account import Account
import zymkey
import binascii
from web3 import Web3
import re

class EthAccount(Account):
    def __init__(self, path: str, address: str, slot: int) -> None:
        self.path = path
        self.address = address
        self.slot = slot

        if not self.is_valid_account():
            raise ValueError("Must provide a valid path, address, and slot")

    def serialize(self) -> dict:
        return {
            "path": self.path,
            "address": self.address,
            "slot": self.slot
        }

    def get_public_key(self) -> str:
        if self.slot < 16 or self.slot > 512:
            raise ValueError("Slot required to be between 16 and 512")
        public_key = zymkey.client.get_public_key(self.slot)
        return '0x' + binascii.hexlify(public_key).decode('utf-8')
    
    def is_valid_account(self) -> bool:

        if not Web3.isChecksumAddress(self.address):
            return False

        if self.slot < 16 or self.slot > 512:
            return False

        bip44_path_pattern = re.compile(r"^m\/44'\/60'\/0'\/0\/\d+$")
        if not bip44_path_pattern.match(self.path):
            return False

        return True
    
    def __repr__(self) -> str:
        return f"(Path: {self.path}, Address: {self.address}, Slot: {self.slot})"
