import sys
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
from ZymbitKeyringManager import ZymbitKeyringManager
import zymkey

options = {
    "wallet_name": "MyExampleWallet"
}

keyring = ZymbitEthKeyring(options)

print(keyring)

keyringManager = ZymbitKeyringManager([keyring])

print(keyringManager.get_keyring(wallet_name="MyExampleWallet"))