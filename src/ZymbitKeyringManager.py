from Keyring import Keyring
from typing import Type
import zymkey

class ZymbitKeyringManager():
    
    def __init__(self, keyrings: list[Keyring] = []) -> None:
        if keyrings:
            for keyring in keyrings:
                if (not issubclass(keyring, Keyring)):
                    raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
            self.keyrings: list[Keyring] = keyrings

    def createKeyring(self, cls: Type[Keyring], walletName: str) -> str:
        if (not issubclass(cls, Keyring)):
            raise TypeError(f"Invalid type: {type(cls)}. Expected a subclass of the Keyring class")

        if(len(walletName) < 1):
             raise TypeError("Invalid walletName")
        
    def addKeyring(self, keyring: Keyring):
        if (not issubclass(keyring, Keyring)):
            raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings.append(keyring)
    
