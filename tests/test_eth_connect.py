import unittest
from unittest.mock import Mock
import sys
import zymkey
import time
from ethconnect import EthConnect, EthTransaction, SignedEthTransaction, ZymbitEthKeyring
from Crypto.Hash import keccak, SHA256

class TestEthConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        cls.slots = list(filter(lambda slot: slot > 15, slots))
        cls.wallet_name = "test_wallet"
        use_bip39_recovery = zymkey.RecoveryStrategyBIP39()
        (master_slot, mnemonic) = zymkey.client.gen_wallet_master_seed(key_type=ZymbitEthKeyring.CURVE.get_curve_type(), master_gen_key=bytearray(), wallet_name=cls.wallet_name, recovery_strategy=use_bip39_recovery)
        cls.master_slot = master_slot
        cls.keyring = ZymbitEthKeyring(wallet_name=cls.wallet_name)
        cls.keyring.add_accounts(5)

    @classmethod
    def tearDownClass(cls):
        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))
        diff = set(slots) - set(cls.slots)
        for slot in list(diff):
            zymkey.client.remove_key(slot)

    def test_create_transaction(self):
        transaction = EthConnect.create_transaction(to=self.keyring.accounts[0].address)
        self.assertIsInstance(transaction, EthTransaction)

    def test_create_deploy_contract_transaction(self):
        transaction = EthConnect.create_deploy_contract_transaction(chain_id=11155111, contract_bytecode_path="./bytecode.txt", contract_abi_path="./ABI.json", constructor_args=['0x'+('0'*64), self.keyring.accounts[0].address])
        self.assertIsInstance(transaction, EthTransaction)

    def test_create_execute_contract_transaction(self):
        transaction = EthConnect.create_execute_contract_transaction(chain_id=11155111, contract_address="0x6FCc62196FD8C0f1a92817312c109D438cC0acC9", contract_abi_path="./ABI.json", function_name="postData", args=["OMRON", "HR_MONITOR", int(time.time()), "0x" + ("0"*64), '0x' + ('0'*130)])
        self.assertIsInstance(transaction, EthTransaction)

    def test_sign_transaction(self):
        transaction = EthConnect.create_transaction(to=self.keyring.accounts[1].address)
        signed_transaction = EthConnect.sign_transaction(transaction, self.keyring, address=self.keyring.accounts[2].address)
        self.assertIsInstance(signed_transaction, SignedEthTransaction)

    def test_rlp_serialize_deserialize_transaction(self):
        transaction = EthConnect.create_transaction(to=self.keyring.accounts[3].address)
        encoded_transaction = EthConnect.rlp_serialize_transaction(transaction)
        decoded_transaction = EthConnect.rlp_deserialize_transaction(encoded_transaction)
        self.assertIsInstance(decoded_transaction, EthTransaction)

    def test_create_sign_message_and_concat_sig(self):
        message, message_bytes = EthConnect.create_message("Hello, World!")
        hash_message = EthConnect.keccak256(bytes_data=message_bytes)
        v, r, s = EthConnect.sign_message(hash_message, self.keyring, address=self.keyring.accounts[3].address)
        self.assertTrue(isinstance(v, int) and isinstance(r, int) and isinstance(s, int))
        signature = EthConnect.concatenate_sig(v,r,s)
        self.assertIsInstance(signature, str)

    def test_keccak256(self):
        keccak_hash = EthConnect.keccak256(str_data="Hello, World!")
        self.assertIsInstance(keccak_hash, keccak.Keccak_Hash)

    def test_sha256(self):
        sha256_hash = EthConnect.sha256(str_data="Hello, World!")
        self.assertIsInstance(sha256_hash, SHA256.SHA256Hash)

    def test_eth_to_wei(self):
        wei = EthConnect.eth_to_wei(ether_amount=1)
        self.assertIsInstance(wei, int)
        self.assertEqual(wei, 1000000000000000000)
