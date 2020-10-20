import binascii
from hashlib import blake2b
from typing import Union

from jumpscale.core.identity import Identity
from jumpscale.loader import j
from nacl.bindings import crypto_scalarmult
from nacl.secret import SecretBox
from nacl.signing import VerifyKey


def encrypt_for_node(identity: Identity, public_key: str, payload: Union[str, bytes]) -> str:
    """
    encrypt payload using a nacl.SecretBox with a shared key derived from the public key of the node and private key of the user

    Args:
      identity(Identity): the identity object that contains the key pair of the user
      public_key(str): public key of the node, hex-encoded
      payload(Union[str, bytes]): any data you want to encrypt

    Returns:
      str: hex-encoded encrypted data. you can use this safely into your reservation data

    """
    user_private = identity.nacl.signing_key.to_curve25519_private_key().encode()

    node_verify_bin = binascii.unhexlify(public_key)
    node_public = VerifyKey(node_verify_bin).to_curve25519_public_key()
    node_public = node_public.encode()

    shared_secret = crypto_scalarmult(user_private, node_public)
    h = blake2b(shared_secret, digest_size=32)
    key = h.digest()

    if isinstance(payload, str):
        payload = payload.encode()

    box = SecretBox(key)
    encrypted = box.encrypt(payload)
    return binascii.hexlify(encrypted)
