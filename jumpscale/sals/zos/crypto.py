import binascii
from typing import Union

from nacl.public import SealedBox
from nacl.signing import VerifyKey


def encrypt_for_node(public_key: str, payload: Union[str, bytes]) -> str:
    """
    encrypt payload with the public key of a node so only the node itself can decrypt it
    use this if you have sensitive data to send in a reservation

    :param public_key: public key of the node, hex-encoded
    :type public_key: str
    :param payload: any data you want to encrypt
    :type payload: Union[str, bytes]
    :return: hex-encoded encrypted data. you can use this safely into your reservation data
    :rtype: str
    """
    node_public_bin = binascii.unhexlify(public_key)
    node_public = VerifyKey(node_public_bin)
    box = SealedBox(node_public.to_curve25519_public_key())

    if isinstance(payload, str):
        payload = payload.encode()

    encrypted = box.encrypt(payload)
    return binascii.hexlify(encrypted)
