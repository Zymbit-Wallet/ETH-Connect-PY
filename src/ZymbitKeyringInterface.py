from abc import ABC, abstractmethod

class ZymbitKeyringInterface(ABC):
    type: str

    def __init__(self, options: dict = {}) -> None:
        self.deserialize(options)

    @abstractmethod
    def serialize(self) -> dict:
        pass

    @abstractmethod
    def deserialize(self, options: dict = {}) -> bool:
        pass

    @abstractmethod
    def addAccounts(self, n: int = 1) -> list[str]:
        pass

    @abstractmethod
    def getAccounts(self) -> list[str]:
        pass

    @abstractmethod
    def removeAccount(self, address: str = None, slot: int = None, path: int = None) -> bool:
        pass


    