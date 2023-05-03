import unittest
from unittest.mock import MagicMock
import sys
from ethconnect import Account, EthAccount
import zymkey
import binascii
from web3 import Web3

class TestEthAccount(unittest.TestCase):

    def test_init(self):
        account = EthAccount("m/44'/60'/0'/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)
        self.assertIsInstance(account, Account)
        self.assertEqual(account.path, "m/44'/60'/0'/0/0")
        self.assertEqual(account.address, "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
        self.assertEqual(account.slot, 32)

    def test_serialize(self):
        account = EthAccount("m/44'/60'/0'/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)
        serialized = account.serialize()
        self.assertEqual(serialized["path"], "m/44'/60'/0'/0/0")
        self.assertEqual(serialized["address"], "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
        self.assertEqual(serialized["slot"], 32)

    def test_is_valid_account(self):
        account = EthAccount("m/44'/60'/0'/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)
        self.assertTrue(account.is_valid_account())

        with self.assertRaises(ValueError):
            invalid_address_account = EthAccount("m/44'/60'/0'/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44", 32)

        with self.assertRaises(ValueError):
            invalid_slot_account = EthAccount("m/44'/60'/0'/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 513)

        with self.assertRaises(ValueError):
            invalid_path_account = EthAccount("m/44'/60'/0'/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)

        with self.assertRaises(ValueError):
            invalid_path_account_2 = EthAccount("m/44'/60'/0'/0/0/0", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)

        with self.assertRaises(ValueError):
            invalid_path_account_3 = EthAccount("m/44'/60'/0'/0/0'", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 32)


