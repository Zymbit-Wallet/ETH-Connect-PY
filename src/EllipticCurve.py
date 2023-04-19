from enum import Enum

class EllipticCurve(Enum):
    secp256k1 = 1
    secp256r1 = 2
    ed25519 = 3