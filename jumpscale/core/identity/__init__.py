import requests

from collections import namedtuple
from nacl.exceptions import CryptoError

from jumpscale.core import exceptions
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.core.config import get_config, update_config
from jumpscale.core.exceptions import Input, Value
from jumpscale.data import serializers
from jumpscale.data.encryption import mnemonic, generate_mnemonic
from jumpscale.data.nacl import NACL
from jumpscale.data.idgenerator import random_int
from jumpscale.data.types import Email
from jumpscale.tools.console import ask_choice, ask_string


class Identity(Base):
    _tid = fields.Integer(default=-1)
    words = fields.Secret()
    email = fields.String()
    tname = fields.String()
    admins = fields.List(fields.String())

    def __init__(
        self,
        tname=None,
        email=None,
        words=None,
        _tid=-1,
        admins=None,
        *args,
        **kwargs,
    ):
        """
        Get Identity

        Requires: tname, email and words or tid and words

        Arguments:
            tname (str, optional): Name eg. example.3bot
            email (str, optional): Email of identity
            words (str): Words used to secure identity
            admins (list of str, optional): Admins

        Raises: NotFound incase tid is passed but does not exists
        Raises: Input: when params are missing
        """
        if not words:
            words = generate_mnemonic()

        super().__init__(
            tname=tname,
            email=email,
            words=words,
            _tid=_tid,
            admins=admins,
            *args,
            **kwargs,
        )

        self._nacl = None
        self.verify_configuration()

    @property
    def nacl(self):
        if not self._nacl:
            seed = mnemonic.mnemonic_to_key(self.words.strip())
            self._nacl = NACL(private_key=seed)
        return self._nacl

    def verify_configuration(self):
        """
        Verifies passed arguments to constructor

        Raises: NotFound incase tid is passed but does not exists
        Raises: Input: when params are missing
        """
        if not self.words:
            raise Input("Words are mandotory for an indentity")
        if self._tid != -1:
            self.register()
        else:
            for key in ["email", "tname"]:
                if not getattr(self, key):
                    raise Value(f"Threebot {key} not configured")

    @property
    def tid(self):
        if self._tid == -1:
            self.register()
        return self._tid

    def register(self, host=None):
        # self.verify_configuration()
        if self.tname not in self.admins:
            self.admins.append(self.tname)
        self._tid = random_int(1, 100000000)
        return self._tid

    def set_default(self):
        from jumpscale.loader import j

        return j.core.identity.set_default(self.instance_name)


def get_identity():
    return IdentityFactory(Identity).me


RESTART_CHOICE = "Restart from the begining"
REENTER_CHOICE = "Re-Enter your value"
CHOICES = [RESTART_CHOICE, REENTER_CHOICE]

IdentityInfo = namedtuple("IdentityInfo", ["identity", "email", "words"])


class Restart(Exception):
    pass


class IdentityFactory(StoredFactory):
    _me = None

    def new(
        self,
        name,
        tname=None,
        email=None,
        words=None,
        tid=-1,
        admins=None,
        **kwargs,
    ):
        instance = super().new(name, tname=tname, email=email, words=words, _tid=tid, admins=admins, **kwargs)
        instance.save()
        return instance

    @property
    def is_configured(self):
        return self._me is not None

    @property
    def me(self):
        if not self._me:
            config = get_config()
            default = config["threebot"]["default"]
            if default:
                self.__class__._me = self.get(name=default)
            else:
                for identity in self.list_all():
                    self.__class__._me = self.get(identity)
                    break
                else:
                    raise Value("No configured identity found")
        return self._me

    def set_default(self, name):
        config = get_config()
        config["threebot"]["default"] = name
        update_config(config)
        self.__class__._me = None

    def get_user(self, tname):
        response = requests.get(f"https://login.threefold.me/api/users/{tname}")
        if response.status_code == 404:
            raise exceptions.NotFound(
                "\nThis identity does not exist in 3bot mobile app connect, Please create an idenity first using 3Bot Connect mobile Application\n"
            )
        return response.json()

    def ask(self):
        """get identity information interactively"""

        def check_email(email):
            # TODO: a way to check/verify email (threefold connect or openkyc?)
            return Email().check(email)

        def with_error(e):
            """used in a loop to re-enter the value or break by raising `Restart` exception"""
            response = ask_choice(f"{e}, What would you like to do? ", CHOICES)
            if response == RESTART_CHOICE:
                raise Restart

        def get_identity_info():
            def fill_words():
                return ask_string("Copy the phrase from your 3bot Connect app here: ")

            def fill_identity():
                identity = ask_string("what is your threebot name (identity)? ")
                if "." not in identity:
                    identity += ".3bot"
                return identity

            user = None
            while not user:
                identity = fill_identity()
                try:
                    user = self.get_user(identity)
                except exceptions.NotFound as e:
                    with_error(e)

            while True:
                email = ask_string("What is the email address associated with your identity? ")
                if check_email(email):
                    break
                else:
                    with_error("This Email address is not valid")

            print("Configured email for this identity is {}".format(email))

            # time to do validation of words
            while True:
                words = fill_words()
                try:
                    seed = mnemonic.mnemonic_to_key(words.strip())
                    key = NACL(seed).get_verification_key()
                    if user and key != serializers.base64.decode(user["publicKey"]):
                        raise exceptions.Input
                    break
                except (exceptions.NotFound, exceptions.Input, CryptoError):
                    with_error("Seems one or more more words entered is invalid")

            return IdentityInfo(identity, email, words)

        while True:
            try:
                return get_identity_info()
            except Restart:
                continue
            except KeyboardInterrupt:
                break


def export_module_as():
    return IdentityFactory(Identity)
