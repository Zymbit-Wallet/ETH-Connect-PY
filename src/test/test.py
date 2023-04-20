import sys
sys.path.append('../')
from ZymbitEthKeyring import ZymbitEthKeyring
import zymkey

options = {
    "walletName": "MyExampleWallet"
}

keyring = ZymbitEthKeyring(options)

print(keyring)