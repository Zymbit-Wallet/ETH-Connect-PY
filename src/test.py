import zymkey
from ZymbitEthKeyring import ZymbitEthKeyring

options = {
    "walletName": "MyExampleWallet"
}

keyring = ZymbitEthKeyring(options)

print(keyring)

(path, walletName, slotNumber) = zymkey.client.get_wallet_node_addr(16)

pubKey = zymkey.client.get_public_key(17)

# keyring.addAccounts(3)
