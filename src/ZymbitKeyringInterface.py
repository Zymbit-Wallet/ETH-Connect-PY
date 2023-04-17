from abc import ABC, abstractclassmethod

class ZymbitKeyringInterface(ABC):
    type: str

    @abstractclassmethod
    def __init__(self, options: dict = {}) -> None:
        self.deserialize(options)

    @abstractclassmethod
    def serialize(self) -> dict:
        pass

    @abstractclassmethod
    def deserialize(self, options: dict = {}) -> bool:
        pass

    @abstractclassmethod
    def addAccounts(self, n: int = 1) -> list[str]:
        pass

    @abstractclassmethod
    def getAccounts(self) -> list[str]:
        pass

    @abstractclassmethod
    def removeAccount(self, address: str = None, slot: int = None, path: int = None) -> bool:
        pass


    