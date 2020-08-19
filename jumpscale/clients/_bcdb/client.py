import json
import base64
from typing import NamedTuple
import requests
from os import path
from jumpscale.clients.base import Client as BaseClient
from urllib.parse import quote_plus
import requests_unixsocket
from jumpscale.core.base import fields
class Object(NamedTuple):
    id: int
    data: bytes
    tags: dict

    @property
    def acl(self):
        return int(self.tags[':acl']) if ':acl' in self.tags else None

    @property
    def size(self):
        return int(self.tags[':size']) if ':size' in self.tags else 0

    @property
    def created(self):
        return int(self.tags[':created']) if ':created' in self.tags else 0

    @property
    def updated(self):
        return int(self.tags[':updated']) if ':updated' in self.tags else 0



class HTTPClient(BaseClient):
    sock = fields.String(default="/tmp/bcdb.sock")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        url = 'http+unix://%s/' % quote_plus(self.sock)
        self.__session = requests_unixsocket.Session()
        self.__url = url

    @property
    def session(self):
        return self.__session

    def headers(self, **args):
        output = {}
        for k, v in args.items():
            if v is None:
                continue
            k = k.replace('_', '-').lower()
            output[k] = str(v)

        return output

    def url(self, *parts):
        return "%s%s" % (self.__url, path.join(*map(str, parts)))

    def collection(self, collection: str, threebot_id: int = None):
        return HTTPBcdbClient(self, collection, threebot_id)

    @property
    def acl(self):
        return HTTPAclClient(self)


class HTTPAclClient:
    def __init__(self, client):
        self.client = client

    @property
    def session(self):
        return self.client.session

    def headers(self, **kwargs):
        return self.client.headers(**kwargs)

    def url(self, *parts):
        url = self.client.url("acl", *parts)
        return url

    def create(self, perm, users):
        """
        create creates an acl with a permission and users

        :param perm: permission to set, formatted as `rwd` replace the missing flag with `-`
                     so a `r--` is readonly. while `rw-` is read/write.
        :param users: list of users to set permission on
        :returns: newly created key
        """

        data = {
            "perm": perm,
            'users': users
        }

        return self.session.post(self.url(), json=data, headers=self.headers()).json()

    def set(self, key, perm):
        """
        set sets a permission to an acl key

        :param key: acl key
        :param perm: permission to set
        :returns: new object id
        """

        data = {
            'perm': perm
        }

        self.session.put(self.url(key), json=data, headers=self.headers())

    def get(self, key):
        """
        get retrieves an acl by key

        :param key: acl key
        :returns: acl object
        """

        return self.session.get(self.url(key), headers=self.headers()).json()

    def grant(self, key, users):
        """
        grants to users

        :param key: acl key
        :param users: users to grant
        :returns: updated id
        """

        data = {
            'users': users
        }

        return self.session.post(self.url(f"{key}/grant"), json=data, headers=self.headers()).json()

    def revoke(self, key, users):
        """
        revoke from users

        :param key: acl key
        :param users: users to revoke
        :returns: updated id
        """

        data = {
            'users': users
        }

        return self.session.post(self.url(f"{key}/revoke"), json=data, headers=self.headers()).json()

    def list(self):
        """
        list all acl's

        :returns: acl list
        """
        response = self.session.get(
            self.url(), headers=self.headers())

        # this should instead read response "stream" and parse each object individually
        content = response.text
        dec = json.JSONDecoder()
        while content:
            obj, idx = dec.raw_decode(content)
            yield obj
            content = content[idx:]


class HTTPBcdbClient:
    def __init__(self, client, collection, threebot_id: int = None):
        self.client = client
        self.collection = collection
        self.threebot_id = threebot_id

    @property
    def session(self):
        return self.client.session

    def url(self, *parts):
        url = self.client.url("db", self.collection, *parts)
        return url

    def headers(self, **kwargs):
        return self.client.headers(x_threebot_id=self.threebot_id, **kwargs)

    def set(self, data, tags: dict = None, acl: int = None):
        """
        set creates a new object given data and tags, and optional acl key.

        :param data: data to set
        :param tags: optional tags associated with the object. useful for find operations
        :param acl: optional acl key
        :returns: new object id
        """

        return self.session.post(
            self.url(),
            data=data,
            headers=self.headers(
                x_acl=acl,
                x_tags=json.dumps(tags) if tags else None,
            ),
        ).json()

    def get(self, key):
        """
        set creates a new object given data and tags, and optional acl key.

        :param data: data to set
        :param tags: optional tags associated with the object. useful for find operations
        :param acl: optional acl key
        :returns: new object id
        """

        response = self.session.get(self.url(key), headers=self.headers())

        return Object(
            id=key,
            data=response.content,
            tags=json.loads(
                response.headers.get('x-tags', 'null')
            ),
        )

    def delete(self, key):
        """
        set creates a new object given data and tags, and optional acl key.

        :param data: data to set
        :param tags: optional tags associated with the object. useful for find operations
        :param acl: optional acl key
        :returns: new object id
        """

        return self.session.delete(self.url(key), headers=self.headers())

    def update(self, key, data: bytes = None, tags: dict = None, acl: int = None):
        return self.session.put(
            self.url(str(key)),
            data=data,
            headers=self.headers(
                x_acl=acl,
                x_tags=json.dumps(tags) if tags else None,
            ),
        )

    def find(self, **kwargs):
        if kwargs is None or len(kwargs) == 0:
            # due to a bug in the warp router (server side)
            # this call does not match if no queries are supplied
            # hence we add a dummy query that is ignred by the server
            kwargs = {'_': ''}

        # this should instead read response "stream" and parse each object individually
        response = self.session.get(
            self.url(), params=kwargs, headers=self.headers())

        content = response.text
        dec = json.JSONDecoder()
        while content:
            obj, idx = dec.raw_decode(content)
            yield Object(
                id=obj['id'],
                tags=obj['tags'],
                data=None,
            )

            content = content[idx:]
