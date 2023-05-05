# Zymbit Wallet Python SDK

## Overview

Blockchain accounts, signatures, and transactions have an additional layer of complexity over traditional cryptographic keys and signatures. The Zymbit Wallet SDK aims to abstract away this complexity, enabling you to create and manage multiple blockchain wallets and seamlessly integrate with various blockchains without having to deal with their technical intricacies. 

The first iteration of the SDK encapsulates all wallet creation, management, and use (sending transactions and interacting with dApps) capabilities for Ethereum and EVM compatible chains.

If you are a developer interested in creating your own custom implementations of Accounts and/or Keyrings to work with ZymbitKeyringManager, you should further explore this repository. By extending the Account and [Keyring Abstract Base Classes (ABCs)](https://docs.python.org/3/library/abc.html), you can implement the required methods and any additional functionality as needed. The elliptic curves we support (secp256k1, secp256r1, and ed25519) are used by many major blockchains, including Bitcoin, Ethereum, Cardano, Solana, and Polkadot. Developing your own keyrings can be incredibly beneficial for a wide range of applications, such as key management or on-chain interactions like sending transactions or interacting with smart contracts.

**NOTE:** Only compatible with [HSM6](https://www.zymbit.com/hsm6/), [SCM](https://www.zymbit.com/scm/), and [SEN](https://www.zymbit.com/secure-compute-node/)

## Installation

```
pip install zymbitwalletsdk
```

## Documentation:

[Zymbit Wallet Python SDK Documentation](https://docs.zymbit.com/zymbit-wallet-sdk/zymbit-wallet-sdk-py/)
