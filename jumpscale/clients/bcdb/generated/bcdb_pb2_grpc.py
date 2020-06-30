# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from . import bcdb_pb2 as bcdb__pb2


class BCDBStub(object):
    """Interface exported by the server.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.Set = channel.unary_unary(
            '/bcdb.BCDB/Set',
            request_serializer=bcdb__pb2.SetRequest.SerializeToString,
            response_deserializer=bcdb__pb2.SetResponse.FromString,
        )
        self.Get = channel.unary_unary(
            '/bcdb.BCDB/Get',
            request_serializer=bcdb__pb2.GetRequest.SerializeToString,
            response_deserializer=bcdb__pb2.GetResponse.FromString,
        )
        self.Update = channel.unary_unary(
            '/bcdb.BCDB/Update',
            request_serializer=bcdb__pb2.UpdateRequest.SerializeToString,
            response_deserializer=bcdb__pb2.UpdateResponse.FromString,
        )
        self.List = channel.unary_stream(
            '/bcdb.BCDB/List',
            request_serializer=bcdb__pb2.QueryRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ListResponse.FromString,
        )
        self.Find = channel.unary_stream(
            '/bcdb.BCDB/Find',
            request_serializer=bcdb__pb2.QueryRequest.SerializeToString,
            response_deserializer=bcdb__pb2.FindResponse.FromString,
        )
        self.Delete = channel.unary_unary(
            '/bcdb.BCDB/Delete',
            request_serializer=bcdb__pb2.DeleteRequest.SerializeToString,
            response_deserializer=bcdb__pb2.DeleteResponse.FromString,
        )


class BCDBServicer(object):
    """Interface exported by the server.
    """

    def Set(self, request, context):
        """Set stores a document and return a header
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Get a document from header
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Modify updates a document meta
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """List returns a list of document IDs that matches a query
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Find(self, request, context):
        """Find like list but return full documents
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BCDBServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Set': grpc.unary_unary_rpc_method_handler(
            servicer.Set,
            request_deserializer=bcdb__pb2.SetRequest.FromString,
            response_serializer=bcdb__pb2.SetResponse.SerializeToString,
        ),
        'Get': grpc.unary_unary_rpc_method_handler(
            servicer.Get,
            request_deserializer=bcdb__pb2.GetRequest.FromString,
            response_serializer=bcdb__pb2.GetResponse.SerializeToString,
        ),
        'Update': grpc.unary_unary_rpc_method_handler(
            servicer.Update,
            request_deserializer=bcdb__pb2.UpdateRequest.FromString,
            response_serializer=bcdb__pb2.UpdateResponse.SerializeToString,
        ),
        'List': grpc.unary_stream_rpc_method_handler(
            servicer.List,
            request_deserializer=bcdb__pb2.QueryRequest.FromString,
            response_serializer=bcdb__pb2.ListResponse.SerializeToString,
        ),
        'Find': grpc.unary_stream_rpc_method_handler(
            servicer.Find,
            request_deserializer=bcdb__pb2.QueryRequest.FromString,
            response_serializer=bcdb__pb2.FindResponse.SerializeToString,
        ),
        'Delete': grpc.unary_unary_rpc_method_handler(
            servicer.Delete,
            request_deserializer=bcdb__pb2.DeleteRequest.FromString,
            response_serializer=bcdb__pb2.DeleteResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'bcdb.BCDB', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


class AclStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary(
            '/bcdb.Acl/Get',
            request_serializer=bcdb__pb2.ACLGetRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLGetResponse.FromString,
        )
        self.Create = channel.unary_unary(
            '/bcdb.Acl/Create',
            request_serializer=bcdb__pb2.ACLCreateRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLCreateResponse.FromString,
        )
        self.List = channel.unary_stream(
            '/bcdb.Acl/List',
            request_serializer=bcdb__pb2.ACLListRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLListResponse.FromString,
        )
        self.Set = channel.unary_unary(
            '/bcdb.Acl/Set',
            request_serializer=bcdb__pb2.ACLSetRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLSetResponse.FromString,
        )
        self.Grant = channel.unary_unary(
            '/bcdb.Acl/Grant',
            request_serializer=bcdb__pb2.ACLUsersRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLUsersResponse.FromString,
        )
        self.Revoke = channel.unary_unary(
            '/bcdb.Acl/Revoke',
            request_serializer=bcdb__pb2.ACLUsersRequest.SerializeToString,
            response_deserializer=bcdb__pb2.ACLUsersResponse.FromString,
        )


class AclServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def Get(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Create(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Set(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Grant(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Revoke(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AclServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Get': grpc.unary_unary_rpc_method_handler(
            servicer.Get,
            request_deserializer=bcdb__pb2.ACLGetRequest.FromString,
            response_serializer=bcdb__pb2.ACLGetResponse.SerializeToString,
        ),
        'Create': grpc.unary_unary_rpc_method_handler(
            servicer.Create,
            request_deserializer=bcdb__pb2.ACLCreateRequest.FromString,
            response_serializer=bcdb__pb2.ACLCreateResponse.SerializeToString,
        ),
        'List': grpc.unary_stream_rpc_method_handler(
            servicer.List,
            request_deserializer=bcdb__pb2.ACLListRequest.FromString,
            response_serializer=bcdb__pb2.ACLListResponse.SerializeToString,
        ),
        'Set': grpc.unary_unary_rpc_method_handler(
            servicer.Set,
            request_deserializer=bcdb__pb2.ACLSetRequest.FromString,
            response_serializer=bcdb__pb2.ACLSetResponse.SerializeToString,
        ),
        'Grant': grpc.unary_unary_rpc_method_handler(
            servicer.Grant,
            request_deserializer=bcdb__pb2.ACLUsersRequest.FromString,
            response_serializer=bcdb__pb2.ACLUsersResponse.SerializeToString,
        ),
        'Revoke': grpc.unary_unary_rpc_method_handler(
            servicer.Revoke,
            request_deserializer=bcdb__pb2.ACLUsersRequest.FromString,
            response_serializer=bcdb__pb2.ACLUsersResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'bcdb.Acl', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


class IdentityStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.Info = channel.unary_unary(
            '/bcdb.Identity/Info',
            request_serializer=bcdb__pb2.InfoRequest.SerializeToString,
            response_deserializer=bcdb__pb2.InfoResponse.FromString,
        )
        self.Sign = channel.unary_unary(
            '/bcdb.Identity/Sign',
            request_serializer=bcdb__pb2.SignRequest.SerializeToString,
            response_deserializer=bcdb__pb2.SignResponse.FromString,
        )


class IdentityServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def Info(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Sign(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IdentityServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Info': grpc.unary_unary_rpc_method_handler(
            servicer.Info,
            request_deserializer=bcdb__pb2.InfoRequest.FromString,
            response_serializer=bcdb__pb2.InfoResponse.SerializeToString,
        ),
        'Sign': grpc.unary_unary_rpc_method_handler(
            servicer.Sign,
            request_deserializer=bcdb__pb2.SignRequest.FromString,
            response_serializer=bcdb__pb2.SignResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'bcdb.Identity', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
