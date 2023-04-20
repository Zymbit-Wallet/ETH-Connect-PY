from Keyring import Keyring
from typing import Type
import zymkey

class ZymbitKeyringManager:
    
    def __init__(self, keyrings: list[Type[Keyring]] = []) -> None:
        if keyrings:
            for keyring in keyrings:
                if not isinstance(keyring, Keyring):
                    raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings: list[Type[Keyring]] = keyrings

    def create_keyring(self, keyring_class: Type[Keyring], wallet_name: str, master_gen_key: bytearray = bytearray()) -> tuple[int, str]:
        if not issubclass(keyring_class, Keyring):
            raise TypeError(f"Invalid type: {type(keyring_class)}. Expected a subclass of the Keyring class")

        if len(wallet_name) < 1 or not isinstance(wallet_name, str):
            raise ValueError("Invalid wallet_name")
        
        if not isinstance(master_gen_key, bytearray):
            raise TypeError("Invalid master_gen_key")
        
        master_key_slot: int = 0
        try:
            use_bip39_recovery = zymkey.RecoveryStrategyBIP39()
            key_type: str = keyring_class.CURVE.get_curve_type()
            master_key: tuple[int, str] = zymkey.client.gen_wallet_master_seed(key_type=key_type, master_gen_key=master_gen_key, wallet_name=wallet_name, recovery_strategy=use_bip39_recovery)
            master_key_slot = master_key[0]

            options = {
                "walletName": wallet_name
            }
            keyring: keyring_class = keyring_class(options)
            self.keyrings.append(keyring)
            return master_key
        except:
            if master_key_slot:
                zymkey.client.remove_key(master_key_slot)

            raise ValueError("Failed to create keyring")
        
    def add_keyring(self, keyring: Type[Keyring]) -> bool:
        if not isinstance(keyring, Keyring):
            raise TypeError(f"Invalid type: {type(keyring)}. Expected a subclass of the Keyring class")
        self.keyrings.append(keyring)
        return True
          
    def get_keyring(self, wallet_name: str = None, master_slot: int = None) -> Type[Keyring]:
        if not (wallet_name or master_slot):
            raise ValueError("wallet_name or master_slot are required")
        
        for keyring in self.keyrings:
            if keyring.wallet_name == wallet_name or keyring.master_slot == master_slot:
                return keyring
            
        raise ValueError("Keyring does not exist in KeyringManager")

    def get_keyrings(self) -> list[Type[Keyring]]:
        return self.keyrings
    
    def remove_keyring(self, wallet_name: str = None, master_slot: int = None, remove_master: bool = False) -> bool:
        if not (wallet_name or master_slot):
            raise ValueError("wallet_name or master_slot are required")
        
        for keyring in self.keyrings:
            if keyring.wallet_name == wallet_name or keyring.master_slot == master_slot:
                slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
                slots = list(filter(lambda slot: slot > 15, slots))
                for slot in slots:
                    (path, curr_wallet_name, curr_master_slot) = zymkey.client.get_wallet_node_addr(slot)
                    if wallet_name == curr_wallet_name or master_slot == curr_master_slot:
                        if (path == 'm' and not remove_master):
                            continue
                        else:
                            zymkey.client.remove_key(slot)
                return True

        return False
        

    
    
