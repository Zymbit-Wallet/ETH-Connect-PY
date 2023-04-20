from enum import Enum

class EllipticCurve(Enum):
    secp256k1 = 1
    secp256r1 = 2
    ed25519 = 3

    def get_curve_type(self) -> str:
        if (self == EllipticCurve.secp256k1):
            return "secp256k1"
        elif (self == EllipticCurve.secp256k1):
            return "secp256r1"
        elif (self == EllipticCurve.ed25519):
            return "ed25519"