def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .s3 import S3Client

    return StoredFactory(S3Client)
