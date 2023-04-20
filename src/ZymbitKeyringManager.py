from Keyring import Keyring
from typing import Type
import zymkey

class ZymbitKeyringManager():
    
    def __init__(self, keyrings: list[Type[Keyring]] = []) -> None:
        if keyrings:
            for keyring in keyrings:
                if (not issubclass(keyring, Type[Keyring])):
                    raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings: list[Type[Keyring]] = keyrings

    def createKeyring(self, keyringClass: Type[Keyring], walletName: str, masterGenKey: bytearray = bytearray()) -> tuple[int, str]:
        if (not issubclass(keyringClass, Keyring)):
            raise TypeError(f"Invalid type: {type(keyringClass)}. Expected a subclass of the Keyring class")

        if (len(walletName) < 1 or not isinstance(walletName, str)):
             raise ValueError("Invalid walletName")
        
        if (not isinstance(masterGenKey, bytearray)):
            raise TypeError("Invalid masterGenKey")
        
        try:
            use_BIP39_recovery = zymkey.RecoveryStrategyBIP39()
            keyType: str = keyringClass.CURVE.getCurveType()
            masterKey: tuple[int, str] = zymkey.client.gen_wallet_master_seed(key_type = keyType, master_gen_key = masterGenKey, wallet_name = walletName, recovery_strategy = use_BIP39_recovery)

            options = {
                "walletName": walletName
            }
            keyring: keyringClass = keyringClass(options)
            self.keyrings.append(keyring)
            return masterKey
        except:
            raise ValueError


    def addKeyring(self, keyring: Type[Keyring]) -> bool:
        if (not issubclass(keyring, Keyring)):
            raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings.append(keyring)
        return True
          
    def getKeyring(self, walletName: str = None, masterSlot: int = None) -> Type[Keyring]:
        if(not (walletName or masterSlot)):
            raise ValueError("walletName or masterSlot are required")
        
        for keyring in self.keyrings:
            if (keyring.walletName == walletName or keyring.masterSlot == masterSlot):
                return keyring
            
        raise ValueError("Keyring does not exist in KeyringManager")

    def getKeyrings(self) -> list[Type[Keyring]]:
        return self.keyrings
    
    def removeKeyring(self, walletName: str = None, masterSlot: int = None, removeMaster: bool = False) -> bool:
        if(not (walletName or masterSlot)):
            raise ValueError("walletName or masterSlot are required")
        
        for keyring in self.keyrings:
            if (keyring.walletName == walletName or keyring.masterSlot == masterSlot):
                slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
                slots = list(filter(lambda slot: slot > 15, slots))
                for slot in slots:
                    (path, currWalletName, currMasterSlot) = zymkey.client.get_wallet_node_addr(slot)
                    if (walletName == currWalletName or masterSlot == currMasterSlot):
                        if (path == 'm'):
                            if (removeMaster):
                                zymkey.client.remove_key(slot)
                            else:
                                continue
                        else:
                            zymkey.client.remove_key(slot)
                return True

        return False
        

    
    
