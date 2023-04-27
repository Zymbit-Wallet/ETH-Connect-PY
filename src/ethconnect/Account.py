from abc import ABC, abstractmethod

class Account(ABC):
    def __init__(self, path: str, slot: int) -> None:
        self.path = path
        self.slot = slot
    
    @abstractmethod
    def serialize(self) -> dict:
        pass
