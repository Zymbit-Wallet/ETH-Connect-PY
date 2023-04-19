from abc import ABC, abstractmethod
from EllipticCurve import EllipticCurve
from Account import Account
import re

class Keyring(ABC):
    TYPE: str
    BASEPATH: str
    CURVE: EllipticCurve

    def __init__(self, options: dict = {}) -> None:
        if (not isinstance(self.CURVE, EllipticCurve)):
            raise TypeError("Invalid elliptic curve type. CURVE should be an instance of the EllipticCurve enumeration.")
        if (not self.isValidBip44BasePath(self.BASEPATH)):
            raise TypeError("Invalid BIP44 BASEPATH")
        self.deserialize(options)

    @abstractmethod
    def serialize(self) -> dict:
        pass

    @abstractmethod
    def deserialize(self, options: dict = {}) -> None:
        pass

    @abstractmethod
    def addAccount(self, index: int = 0) -> Account:
        pass

    @abstractmethod
    def addAccounts(self, n: int = 1) -> list[Account]:
        pass

    @abstractmethod
    def getAccounts(self) -> list[Account]:
        pass

    @abstractmethod
    def removeAccount(self, address: str = None, slot: int = None, path: int = None) -> bool:
        pass

    @staticmethod
    def isValidBip44BasePath(s: str) -> bool:
        pattern = r"^m\/\d+'\/\d+'\/\d+'\/\d+$"
        return bool(re.match(pattern, s)) and " " not in s


    