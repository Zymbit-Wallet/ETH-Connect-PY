from abc import ABC, abstractmethod
from .EllipticCurve import EllipticCurve
from typing import Type
from .Account import Account
import re

class Keyring(ABC):
    TYPE: str
    BASE_PATH: str
    CURVE: EllipticCurve

    def __init__(self, wallet_name: str = None, master_slot: int = None) -> None:
        if not isinstance(self.CURVE, EllipticCurve):
            raise TypeError("Invalid elliptic curve type. CURVE should be an instance of the EllipticCurve enumeration.")
        if not self._is_valid_bip44_base_path(self.BASE_PATH):
            raise TypeError("Invalid BIP44 BASE_PATH")
        self.deserialize(wallet_name=wallet_name, master_slot=master_slot)
        if not (hasattr(self, 'wallet_name') and hasattr(self, 'master_slot')):
            raise TypeError("Subclasses of Keyring must have instance properties 'wallet_name' and 'master_slot'")

    @abstractmethod
    def serialize(self) -> dict:
        pass

    @abstractmethod
    def deserialize(self, wallet_name: str = None, master_slot: int = None) -> bool:
        pass

    @abstractmethod
    def add_account(self, index: int = 0) -> Account:
        pass

    @abstractmethod
    def add_accounts(self, n: int = 1) -> list[Account]:
        pass

    @abstractmethod
    def get_accounts(self) -> list[Account]:
        pass

    @abstractmethod
    def remove_account(self, address: str = None, slot: int = None, path: int = None) -> bool:
        pass

    @staticmethod
    def _is_valid_bip44_base_path(s: str) -> bool:
        pattern = r"^m\/\d+'\/\d+'\/\d+'\/\d+$"
        return bool(re.match(pattern, s)) and " " not in s
