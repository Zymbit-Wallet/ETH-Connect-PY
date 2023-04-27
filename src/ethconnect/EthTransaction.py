import rlp
from rlp.sedes import binary, Binary, big_endian_int, BigEndianInt, List, CountableList, boolean

access_list_sede_type = CountableList(List([Binary.fixed_length(20, allow_empty=False), CountableList(BigEndianInt(32)),]),)

# Transaction EIP-1559 
class EthTransaction(rlp.Serializable):
    transaction_type = 2

    fields = [
        ("chain_id", big_endian_int),
        ("nonce", big_endian_int),
        ("max_priority_fee_per_gas", big_endian_int),
        ("max_fee_per_gas", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("access_list", access_list_sede_type),
    ]

# Signed Transaction EIP-1559 
class SignedEthTransaction(rlp.Serializable):
    transaction_type = 2

    fields = [
        ("chain_id", big_endian_int),
        ("nonce", big_endian_int),
        ("max_priority_fee_per_gas", big_endian_int),
        ("max_fee_per_gas", big_endian_int),
        ("gas", big_endian_int),
        ("to", Binary.fixed_length(20, allow_empty=True)),
        ("value", big_endian_int),
        ("data", binary),
        ("access_list", access_list_sede_type),
        ("y_parity", boolean),
        ("r", big_endian_int),
        ("s", big_endian_int),
    ]
