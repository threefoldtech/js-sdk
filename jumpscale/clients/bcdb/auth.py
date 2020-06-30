import base64
import time
import json
import grpc

from typing import NamedTuple

from mnemonic import Mnemonic
from nacl.signing import SigningKey

EnglishMnemonic = Mnemonic("english")


class Identity:
    def __init__(self, id, signing_key):
        self.__id = id
        self.__signing_key = signing_key

    @classmethod
    def from_seed(cls, tid, words):
        """
        Provide a path to a seed file as generated by the tfuser tool
        """
        entropy = EnglishMnemonic.to_entropy(words)
        signing_key = SigningKey(bytes(entropy))

        return cls(tid, signing_key)

    def id(self):
        return self.__id

    def sign(self, message):
        """
        sign message, return signature
        """
        return self.__signing_key.sign(message).signature

    def sign_base64(self, message):
        """
        sign message, return the signature in base64 encoding
        """
        return base64.standard_b64encode(self.sign(message)).decode()


# from https://github.com/grpc/grpc/tree/master/examples/python/auth
class AuthGateway(grpc.AuthMetadataPlugin):
    def __init__(self, identity, expires):
        self.identity = identity
        self.expires = expires

    def get_auth_header(self):
        created = int(time.time())
        expires = created + self.expires

        headers = f"(created): {created}\n"
        headers += f"(expires): {expires}\n"
        headers += f"(key-id): {self.identity.id()}"

        signature = self.identity.sign_base64(headers.encode())

        auth_header = f'Signature keyId="{self.identity.id()}",algorithm="hs2019",created="{created}",expires="{expires}",headers="(created) (expires) (key-id)",signature="{signature}"'
        return "authorization", auth_header

    def __call__(self, context, callback):
        """Implements authentication by passing metadata to a callback.
        Implementations of this method must not block.
        Args:
        context: An AuthMetadataContext providing information on the RPC that
            the plugin is being called to authenticate.
        callback: An AuthMetadataPluginCallback to be invoked either
            synchronously or asynchronously.
        """
        callback((self.get_auth_header(),), None)
