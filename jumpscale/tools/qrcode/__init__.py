import pyqrcode


def _get_qr_object(content, version, mode, encoding):
    return pyqrcode.create(content, version=version, mode=mode, encoding=encoding)


def png_get(content, file_path, version=None, mode=None, encoding=None, scale=1):
    """Writes QR code to file in PNG format

    Args:
        content (str): content to be encoded
        file_path (str): file path to write to
        version (int, optional): data capacity of the code, automatic if not specified. Defaults to None.
        mode (str, optional): how the content will be encoded, automatic if not specified. Defaults to None.
        encoding (str, optional): Encoding of the specfied content string. Defaults to None.
        scale (int, optional): scale of the QR code relative to the module. Defaults to 1.
    """
    qr_object = _get_qr_object(content, version, mode, encoding)
    qr_object.png(file_path, scale=scale)


def svg_get(content, file_path, version=None, mode=None, encoding=None, scale=1, title=None):
    """Writes QR code to file in SVG format

    Args:
        content (str): content to be encoded
        file_path (str): file path to write to
        version (int, optional): data capacity of the code, automatic if not specified. Defaults to None.
        mode (str, optional): how the content will be encoded, automatic if not specified. Defaults to None.
        encoding (str, optional): Encoding of the specfied content string. Defaults to None.
        scale (int, optional): scale of the QR code relative to the module. Defaults to 1.
        title (str, optional): title of the SVG. Defauls to None.
    """
    qr_object = _get_qr_object(content, version, mode, encoding)
    qr_object.svg(file_path, scale=scale, title=title)


def base64_get(content, version=None, mode=None, encoding=None, scale=1):
    """returns base 64 of QR code

    Args:
        content (str): content to be encoded
        version (int, optional): data capacity of the code, automatic if not specified. Defaults to None.
        mode (str, optional): how the content will be encoded, automatic if not specified. Defaults to None.
        encoding (str, optional): Encoding of the specfied content string. Defaults to None.
        scale (int, optional): scale of the QR code relative to the module. Defaults to 1.
    """
    qr_object = _get_qr_object(content, version, mode, encoding)
    return qr_object.png_as_base64_str(scale=scale)
