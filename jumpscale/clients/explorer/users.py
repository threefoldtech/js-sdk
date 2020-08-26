from typing import Iterator, List

from jumpscale.core import identity
from jumpscale.core.exceptions import NotFound

from .base import BaseResource
from .models import User
from .pagination import get_all, get_page


def _build_query(name: str = None, email: str = None) -> dict:
    query = {}
    if name is not None:
        query["name"] = name
    if email is not None:
        query["email"] = email
    return query


class Users(BaseResource):
    _resource = "users"

    def iter(self, name: str = None, email=None) -> Iterator:
        """
        Iterate over the users of the grid

        :param name: filter by name
        :type name: str, optional
        :param email: filter by email
        :type email: str, optional
        :yield: return an iterator yielding users
        :rtype: iterator
        """
        query = _build_query(name=name, email=email)
        yield from get_all(self._session, User, self._url, query)

    def list(self, name: str = None, email: str = None, page=None) -> List[User]:
        """
        list all users of the grid

        :param name: filter by name
        :type name: str, optional
        :param email: filter by email
        :type email: str, optional
        :yield: return a list of User
        :rtype: list
        """
        query = _build_query(name=name, email=email)
        if page:
            users, _ = get_page(self._session, page, User, self._url, query)
        else:
            users = list(self.iter(name=name, email=email))
        return users

    def new(self) -> User:
        """
        create an empty User object

        :return: User
        :rtype: User
        """
        return User()

    def register(self, user) -> int:
        """
        register a new user on the explorer

        :param user: User
        :type user: User
        :return: the new user ID
        :rtype: int
        """
        resp = self._session.post(self._url, json=user.to_dict())
        return resp.json()["id"]

    def validate(self, tid, payload, signature):
        url = self._url + f"/users/{tid}/validate"
        data = {
            "payload": payload,
            "signature": signature,
        }

        resp = self._session.post(url, json=data)
        return resp.json()["is_valid"]

    def update(self, user: User) -> None:
        """
        Update user information

        the updatable fields are:
        email
        pubkey
        host
        description

        :param user: User
        :type user: User
        """
        me = identity.get_identity()
        datatosign = ""
        datatosign += f"{user.id}{user.name}{user.email}"
        if user.host:
            datatosign += user.host
        datatosign += f"{user.description}{user.pubkey}"
        signature = me.nacl.sign_hex(datatosign.encode("utf8"))
        data = user.to_dict().copy()
        data["sender_signature_hex"] = signature.decode("utf8")
        self._session.put(f"{self._url}/{user.id}", json=data)

    def get(self, tid: int = None, name: str = None, email: str = None) -> User:
        """
        get the detail of a specific user

        :param tid: search by ID
        :type tid: int, optional
        :param name: search by name, defaults to None
        :type name: str, optional
        :param email: search by email, defaults to None
        :type email: str, optional
        :raises NotFound: if not user found with the specified filters
        :return: User
        :rtype: User
        """
        if tid is not None:
            resp = self._session.get(f"{self._url}/{tid}")
            return User.from_dict(resp.json())

        results = self.list(name=name, email=email)
        if results:
            return results[0]
        raise NotFound("user not found")
