import binascii
from nacl import public
from nacl.encoding import Base64Encoder
from nacl.signing import VerifyKey


def generate_zos_keys(node_public_key):
    """Generate a new set of wireguard key pair and encrypt
       the private side using the public key of a 0-OS node.

    Args:
        node_public_key (str): hex encoded public key of 0-OS node.
                                  This is the format you find in the explorer

    Returns:
        tuple: tuple containing 3 fields (private key, private key encrypted, public key)
    """
    wg_private = public.PrivateKey.generate()
    wg_public = wg_private.public_key

    wg_private_base64 = wg_private.encode(Base64Encoder)
    wg_public_base64 = wg_public.encode(Base64Encoder)

    node_public_bin = binascii.unhexlify(node_public_key)
    node_public = VerifyKey(node_public_bin)
    box = public.SealedBox(node_public.to_curve25519_public_key())

    wg_private_encrypted = box.encrypt(wg_private_base64)
    wg_private_encrypted_hex = binascii.hexlify(wg_private_encrypted)

    return (wg_private_base64.decode(), wg_private_encrypted_hex.decode(), wg_public_base64.decode())


def generate_key_pair():
    wg_private = public.PrivateKey.generate()
    wg_public = wg_private.public_key

    wg_private_base64 = wg_private.encode(Base64Encoder)
    wg_public_base64 = wg_public.encode(Base64Encoder)
    return wg_private_base64, wg_public_base64
