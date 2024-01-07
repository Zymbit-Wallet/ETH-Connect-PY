from .Account import Account
import zymkey
import binascii
import re
import base58
import bech32

class BtcAccount(Account):
    __MAINNET_PATH_PATTERN = re.compile(r"^m\/44'\/0'\/[0-1]'\/[0-1]\/[0-9]+$")
    __TESTNET_PATH_PATTERN = re.compile(r"^m\/44'\/1'\/[0-1]'\/[0-1]\/[0-9]+$")

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
        if not BtcAccount._is_valid_btc_address(self.address):
            return False

        if self.slot < 16 or self.slot > 512:
            return False

        # Determine if the address is for mainnet or testnet
        is_testnet = self.address.startswith('m') or self.address.startswith('n') or self.address.startswith('2') or self.address.startswith('tb1')

        # Check if the path matches the address type
        if is_testnet:
            return bool(BtcAccount.__TESTNET_PATH_PATTERN.match(self.path))
        else:
            return bool(BtcAccount.__MAINNET_PATH_PATTERN.match(self.path))


    @staticmethod
    def _is_valid_btc_address(address) -> bool:
        if len(address) < 26 or len(address) > 35:
            return False

        if address.startswith('1') or address.startswith('3') or address.startswith('m') or address.startswith('n') or address.startswith('2'):
            try:
                base58.b58decode_check(address)
                return True
            except ValueError:
                return False

        if address.startswith('bc1') or address.startswith('tb1'):
            try:
                _, data = bech32.bech32_decode(address)
                return data is not None
            except ValueError:
                return False

        return False

    def __repr__(self) -> str:
        return f"(Path: {self.path}, Address: {self.address}, Slot: {self.slot})"
