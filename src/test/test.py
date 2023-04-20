import sys
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
from ZymbitKeyringManager import ZymbitKeyringManager
import zymkey

keyringManager = ZymbitKeyringManager()

print(keyringManager.createKeyring(ZymbitEthKeyring, "MyExampleWallet"))

print(keyringManager.getKeyring(walletName="MyExampleWallet"))

# options = {
#     "walletName": "MyExampleWallet"
# }

# keyring = ZymbitEthKeyring(options)

# print(keyring)