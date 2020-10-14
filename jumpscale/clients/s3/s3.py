from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields
import urllib3
import certifi

from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists


class S3Client(Client):
    name = fields.String()
    address = fields.String()
    port = fields.Integer()
    access_key = fields.String()
    secret_key = fields.String()
    bucket = fields.String()
    create_bucket = fields.Boolean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the http client to be able to set timeout
        http_client = urllib3.PoolManager(
            timeout=5,
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where(),
            retries=urllib3.Retry(total=3, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504]),
        )
        # Create Minio client
        self.client = Minio(
            "{}:{}".format(self.address, self.port),
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
            http_client=http_client,
        )

        if self.create_bucket:
            self._bucket_create(self.bucket)

    def _bucket_create(self, name):
        try:
            self.client.make_bucket(name, location="us-east-1")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise

    def upload(self, bucket_name, object_name, file_path, content_type="text/plain", meta_data=None):
        """Upload contents from a file specified by file_path, to object_name

        :param bucket_name: name of bucket
        :type bucket_name: str
        :param object_name: name of object
        :type object_name: str
        :param file_path: local path from which object data will be read
        :type file_path: str
        :param content_type: content type of the object, defaults to 'text/plain'
        :type content_type: str, optional
        :param meta_data: additional metadata, defaults to None
        :type meta_data: dict, optional
        :raises ValueError: if file given by file_path is not found
        :return: str
        :rtype: Object etag computed by the minio server.
        """
        if not j.sals.fs.exists(file_path):
            raise j.exceptions.Value("file: {} not found".format(file_path))
        return self.client.fput_object(bucket_name, object_name, file_path, content_type, meta_data)

    def download(self, bucket_name, object_name, file_path):
        """Download and save the object as a file in the local filesystem

        :param bucket_name: name of bucket
        :type bucket_name: str
        :param object_name: name of object
        :type object_name: str
        :param file_path: local path to which object data will be written
        :type file_path: str
        :return: object stat info (includes: size, etag, content_type,last_modified, metadata)
        :rtype: Object
        """

        return self.client.fget_object(bucket_name, object_name, file_path)

    def list_buckets(self):
        """List all buckets

        :return: bucketList, bucket.name, bucket.creation_date
        :rtype: function, str, date
        """
        return self.client.list_buckets()

    def list_objects(self, bucket_name, prefix=None, recursive=None):
        """List objects in a specific bucket

        :param bucket_name: name of bucket
        :type bucket_name: str
        :param prefix: prefix of the objects that should be listed, defaults to None
        :type prefix: str, optional
        :param recursive: True indicates recursive style listing and False indicates directory style listing delimited by '/', defaults to None
        :type recursive: bool, optional
        :return: Iterator for all the objects in the bucket (includes: bucket_name, object_name,is_dir, size, etag, last_modified)
        :rtype: Object
        """

        return self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)

    def remove_bucket(self, bucket_name):
        """Remove a bucket.

        :param bucket_name: name of bucket to be removed
        :type bucket_name: str
        """
        return self.client.remove_bucket(bucket_name)

    def remove_object(self, bucket_name, object_name):
        """Remove object from bucket

        :param bucket_name: name of bucket
        :type bucket_name: str
        :param object_name: name of object to be removed
        :type object_name: str
        """

        return self.client.remove_object(bucket_name, object_name)
