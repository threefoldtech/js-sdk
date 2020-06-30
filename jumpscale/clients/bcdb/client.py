import json
from .auth import AuthGateway
from nacl.signing import SigningKey
from .generated import bcdb_pb2 as types
from .generated.bcdb_pb2_grpc import BCDBStub, AclStub
import base64
import grpc
from typing import NamedTuple
import requests
from os import path
from jumpscale.clients.base import Client as BaseClient
from urllib.parse import quote_plus
import requests_unixsocket
from jumpscale.core.base import fields
from .auth import Identity

class AclClient(BaseClient):
    def __init__(self, channel):
        self.__stub = AclStub(channel)

    def create(self, perm: str = 'r--', users: list = None):
        """
        :param perm: string in format `rwd`, set the missing permission to `-`
        """
        request = types.ACLCreateRequest(
            acl=types.ACL(
                perm=perm,
                users=users
            )
        )
        return self.__stub.Create(request).key

    def list(self):
        """
        lists all acl objects
        """
        return self.__stub.List(types.ACLListRequest())

    def get(self, key: int):
        """
        gets an acl object given key
        """
        request = types.ACLGetRequest(key=key)
        return self.__stub.Get(request).acl

    def set(self, key: int, perm: str):
        """
        update an acl permissions string
        """
        request = types.ACLSetRequest(
            key=key,
            perm=perm,
        )

        self.__stub.Set(request)

    def grant(self, key: int, users: list):
        """
        grant new users to the acl group
        """
        request = types.ACLUsersRequest(
            key=key,
            users=users,
        )

        self.__stub.Grant(request)

    def revoke(self, key: int, users: list):
        """
        removes users from an acl group
        """
        request = types.ACLUsersRequest(
            key=key,
            users=users,
        )

        self.__stub.Revoke(request)


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


class BcdbClient(BaseClient):
    def __init__(self, channel, collection, threebot_id: int = None):
        self.__metadata = None if threebot_id is None else (
            ("x-threebot-id", str(threebot_id)),)

        self.__stub = BCDBStub(channel)
        self.__collection = collection

    @property
    def collection(self):
        return self.__collection

    def __tags_from_meta(self, metadata):
        tags = dict()
        for tag in metadata.tags:
            tags[tag.key] = tag.value

        return tags

    def get(self, id: int) -> Object:
        """
        gets an object given object id
        """
        request = types.GetRequest(
            collection=self.collection,
            id=id,
        )

        response = self.__stub.Get(request, metadata=self.__metadata)
        tags = self.__tags_from_meta(response.metadata)

        return Object(
            id=id,
            data=response.data,
            tags=tags
        )

    def set(self, data: bytes, tags: dict = None, acl: int = None):
        """
        set creates a new object given data and tags, and optional acl key.

        :param data: data to set
        :param tags: optional tags associated with the object. useful for find operations
        :param acl: optional acl key
        :returns: new object id
        """
        _tags = list()
        for k, v in tags.items():
            _tags.append(
                types.Tag(key=k, value=v)
            )

        request = types.SetRequest(
            data=data,
            metadata=types.Metadata(
                collection=self.collection,
                acl=None if acl is None else types.AclRef(acl=acl),
                tags=_tags,
            )
        )

        return self.__stub.Set(request, metadata=self.__metadata).id

    def update(self, id: int, data: bytes = None, tags: dict = None, acl: int = None):
        """
        Update object given object id.

        :param data: optional update object data
        :param tags: optional update tags. new tags will override older tag values that has
                     the same tag name, new tags will be appended.
        :param acl: optional override object acl. note that only owner can set this field
                    even if the caller has a write permission on the object
        """
        _tags = list()
        for k, v in tags.items():
            _tags.append(
                types.Tag(key=k, value=v)
            )

        request = types.UpdateRequest(
            id=id,
            data=None if data is None else types.UpdateRequest.UpdateData(
                data=data),
            metadata=types.Metadata(
                collection=self.collection,
                acl=None if acl is None else types.AclRef(acl=acl),
                tags=_tags,
            )
        )

        self.__stub.Update(request, metadata=self.__metadata)

    def delete(self, id: int):
        """
        Mark the object as deleted
        """
        request = types.DeleteRequest(
            id=id,
            collection=self.collection,
        )

        self.__stub.Delete(request, metadata=self.__metadata)

    def list(self, **matches):
        """
        List all object ids that matches given tags
        """
        tags = list()
        for k, v in matches.items():
            tags.append(
                types.Tag(key=k, value=v)
            )

        request = types.QueryRequest(
            collection=self.collection,
            tags=tags,
        )

        for result in self.__stub.List(request, metadata=self.__metadata):
            yield result.id

    def find(self, **matches):
        """
        Find all objects that matches given tags

        Note: returned objects from fiend does not include data. so object.data will always be None
              to get the object data you will have to do a separate call to .get(id)
        """
        tags = list()
        for k, v in matches.items():
            tags.append(
                types.Tag(key=k, value=v)
            )

        request = types.QueryRequest(
            collection=self.collection,
            tags=tags,
        )

        for result in self.__stub.Find(request, metadata=self.__metadata):
            yield Object(
                id=result.id,
                data=None,
                tags=self.__tags_from_meta(result.metadata),
            )


class Client(BaseClient):
    address = fields.URL(default="http://127.0.0.1")
    port = fields.Integer(default=50051)
    identity = fields.Object(Identity)
    ssl = fields.Boolean(default=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auth_gateway = AuthGateway(self.identity, 3)
        call_cred = grpc.metadata_call_credentials(
            auth_gateway, name="bcdb-auth-gateway")

        # channel_cred = None
        # if ssl:
        #     channel_cred = grpc.ssl_channel_credentials()
        # else:
        channel_cred = grpc.local_channel_credentials()

        credentials = grpc.composite_channel_credentials(
            channel_cred, call_cred)
        channel = grpc.secure_channel(f"{self.address}:{self.port}", credentials)

        self.__channel = channel
        self.__acl = AclClient(channel)

    @property
    def acl(self):
        return self.__acl

    def collection(self, collection: str, threebot_id: int = None) -> BcdbClient:
        """
        Return a bcdb client

        :threebot_id: which threebot id instance to use, if None, use the
                      one directly connected to by this client
        """
        return BcdbClient(self.__channel, collection, threebot_id)


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
