import unittest
from typing import Type
import zymkey
import sys
from ethconnect import Keyring, ZymbitEthKeyring, ZymbitKeyringManager


class ZymbitEthKeyringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a zymbit keyring manager instance
        cls.keyring_manager = ZymbitKeyringManager()

    def test_create_and_remove_keyring(self):
        # test that a keyring can be created with valid inputs
        wallet_name_1 = "test_wallet_1"
        wallet_name_2 = "test_wallet_2"
        master_gen_key = bytearray([0x03] * 32)
        master_slot, mnemonic = self.keyring_manager.create_keyring(ZymbitEthKeyring, wallet_name_1, master_gen_key)
        master_slot1, mnemonic1 = self.keyring_manager.create_keyring(ZymbitEthKeyring, wallet_name_2)
        self.assertIsInstance(master_slot, int)
        self.assertIsInstance(mnemonic, str)
        self.assertEqual(len(mnemonic.split()), 24)
        self.assertIsInstance(master_slot1, int)
        self.assertIsInstance(mnemonic1, str)
        self.assertEqual(len(mnemonic1.split()), 24)

        keyrings = self.keyring_manager.get_keyrings()
        self.assertEqual(len(keyrings), 2)

        # test that creating a keyring with an invalid keyring class raises a AttributeError and ValueError
        with self.assertRaises(AttributeError) and self.assertRaises(ValueError):
            self.keyring_manager.create_keyring(Keyring, wallet_name_1, master_gen_key)

        # test that creating a keyring with an invalid wallet name raises a ValueError
        with self.assertRaises(ValueError):
            self.keyring_manager.create_keyring(ZymbitEthKeyring, "", master_gen_key)

        # test that creating a keyring with an invalid master_gen_key raises a TypeError
        with self.assertRaises(TypeError):
            self.keyring_manager.create_keyring(ZymbitEthKeyring, wallet_name_1, "invalid_key")

        self.keyring_manager.remove_keyring(wallet_name_1, remove_master=True)
        self.keyring_manager.remove_keyring(wallet_name_2, remove_master=True)

    def test_add_and_remove_keyring(self):
        # create a new keyring and add it to the manager
        wallet_name = "test_wallet_3"
        use_bip39_recovery = zymkey.RecoveryStrategyBIP39()
        zymkey.client.gen_wallet_master_seed(key_type=ZymbitEthKeyring.CURVE.get_curve_type(), master_gen_key=bytearray(), wallet_name=wallet_name, recovery_strategy=use_bip39_recovery)
        keyring = ZymbitEthKeyring(wallet_name=wallet_name)
        self.keyring_manager.add_keyring(keyring)

        # test that the keyring was added successfully
        added_keyring = self.keyring_manager.get_keyring(wallet_name)
        self.assertIsInstance(added_keyring, ZymbitEthKeyring)
        self.assertEqual(added_keyring.wallet_name, wallet_name)

        # remove the keyring and test that it was removed successfully
        self.keyring_manager.remove_keyring(wallet_name, remove_master=True)
        with self.assertRaises(ValueError):
            self.keyring_manager.get_keyring(wallet_name)

        
