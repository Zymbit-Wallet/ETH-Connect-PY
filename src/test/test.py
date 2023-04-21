import sys
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
from ZymbitKeyringManager import ZymbitKeyringManager
import zymkey

options = {
    "wallet_name": "MyExampleWallet"
}

keyring = ZymbitEthKeyring(options)

options = {
    "wallet_name": "MyExampleWallet1"
}

keyring1 = ZymbitEthKeyring(options)

keyringManager = ZymbitKeyringManager([keyring, keyring1])

print(keyringManager.get_keyrings())