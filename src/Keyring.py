from abc import ABC, abstractmethod
from Account import Account

class Keyring(ABC):
    TYPE: str
    BASEPATH: str

    def __init__(self, options: dict = {}) -> None:
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


    