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

    def createKeyring(self, keyringClass: Type[Keyring], walletName: str, masterGenKey: bytearray = bytearray()) -> tuple[int, str]:
        if (not issubclass(keyringClass, Keyring)):
            raise TypeError(f"Invalid type: {type(keyringClass)}. Expected a subclass of the Keyring class")

        if(len(walletName) < 1):
             raise TypeError("Invalid walletName")
        
        if(not isinstance(masterGenKey, bytearray)):
            raise TypeError("Invalid masterGenKey")

        use_BIP39_recovery = zymkey.RecoveryStrategyBIP39()
        keyType = keyringClass.CURVE.getCurveType()
        masterKey = zymkey.client.gen_wallet_master_seed(key_type = keyType, master_gen_key = masterGenKey, wallet_name = walletName, recovery_strategy = use_BIP39_recovery)

        options = {
            "walletName": walletName,
        }
        keyring: keyringClass = keyringClass(options)
        self.keyrings.append(keyring)

        return masterKey


    def addKeyring(self, keyring: Keyring):
        if (not issubclass(keyring, Keyring)):
            raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings.append(keyring)
    
