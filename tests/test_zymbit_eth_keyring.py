import unittest
from unittest.mock import patch
from Crypto.Hash import SHA256, keccak
from typing import List
import sys
import zymkey
from ethconnect import Keyring, EthAccount, EllipticCurve, EthTransaction, SignedEthTransaction, ZymbitEthKeyring


class TestZymbitEthKeyring(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        cls.slots = list(filter(lambda slot: slot > 15, slots))
        cls.wallet_name = "test_wallet"
        use_bip39_recovery = zymkey.RecoveryStrategyBIP39()
        (master_slot, mnemonic) = zymkey.client.gen_wallet_master_seed(key_type=ZymbitEthKeyring.CURVE.get_curve_type(), master_gen_key=bytearray(), wallet_name=cls.wallet_name, recovery_strategy=use_bip39_recovery)
        cls.master_slot = master_slot
        cls.keyring = ZymbitEthKeyring(master_slot=master_slot)

    @classmethod
    def tearDownClass(cls):
        slots: list[int] = zymkey.client.get_slot_alloc_list()[0]
        slots = list(filter(lambda slot: slot > 15, slots))
        diff = set(slots) - set(cls.slots)
        for slot in list(diff):
            zymkey.client.remove_key(slot)
        
    def test_serialize_deserialize(self):
        serialized = self.keyring.serialize()
        keyring = ZymbitEthKeyring(wallet_name=serialized['wallet_name'])
        self.assertEqual(self.keyring.TYPE, keyring.TYPE)
        self.assertEqual(self.keyring.BASE_PATH, keyring.BASE_PATH)
        self.assertEqual(self.keyring.wallet_name, keyring.wallet_name)
        self.assertEqual(self.keyring.master_slot, keyring.master_slot)
        self.assertEqual(self.keyring.base_slot, keyring.base_slot)
        self.assertEqual(len(self.keyring.accounts), len(keyring.accounts))

    def test_add_account(self):
        self.assertEqual(len(self.keyring.accounts), 0)
        new_account = self.keyring.add_account()
        self.assertEqual(len(self.keyring.accounts), 1)
        self.assertIsInstance(new_account, EthAccount)
        self.assertEqual(new_account.path, "m/44'/60'/0'/0/0")

    def test_add_accounts(self):
        self.assertEqual(len(self.keyring.accounts), 1)
        new_accounts = self.keyring.add_accounts(3)
        self.assertEqual(len(self.keyring.accounts), 4)
        self.assertIsInstance(new_accounts, list)
        self.assertIsInstance(new_accounts[0], EthAccount)
        self.assertEqual(new_accounts[0].path, "m/44'/60'/0'/0/1")
        self.assertEqual(new_accounts[1].path, "m/44'/60'/0'/0/2")
        self.assertEqual(new_accounts[2].path, "m/44'/60'/0'/0/3")

    def test_add_accounts_list(self):
        self.assertEqual(len(self.keyring.accounts), 4)
        new_accounts = self.keyring.add_accounts_list([4, 20, 7])
        self.assertEqual(len(self.keyring.accounts), 7)
        self.assertIsInstance(new_accounts, list)
        self.assertIsInstance(new_accounts[0], EthAccount)
        self.assertEqual(new_accounts[0].path, "m/44'/60'/0'/0/4")
        self.assertEqual(new_accounts[1].path, "m/44'/60'/0'/0/20")
        self.assertEqual(new_accounts[2].path, "m/44'/60'/0'/0/7")

    def test_get_accounts(self):
        self.assertEqual(len(self.keyring.accounts), 7)
        new_account = self.keyring.add_account(index=35)
        accounts = self.keyring.get_accounts()
        self.assertEqual(len(accounts), 8)
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], EthAccount)
        self.assertEqual(accounts[-1].path,"m/44'/60'/0'/0/35")

    def test_remove_account(self):
        account = self.keyring.get_accounts()[0]
        self.assertEqual(len(self.keyring.accounts), 8)
        self.assertTrue(self.keyring.remove_account(address=account.address))
        self.assertEqual(len(self.keyring.accounts), 7)

    def test_get_public_key(self):
        account = self.keyring.get_accounts()[0]
        public_key = self.keyring.get_public_key(address=account.address)
        self.assertIsInstance(public_key, str)
        self.assertRegex(public_key, r'^0x[a-fA-F0-9]{128}$')
