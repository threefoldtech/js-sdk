"""Module to convert byte-strings."""

import binascii
import struct


def float2int_ensure_precision(value, scale):
    """Cast a float to an int with the given scale but ensure the best precision."""

    # Round it to make sure we have the utmost precision
    return int(round(value * pow(10.0, scale)))


def int2float_ensure_precision(value, scale):
    """Cast an int to a float with the given scale but ensure that the values (up to the scale) are correct.
    eg. 42112588 with scale 4 should certainly render: 4211.2588 and not 4211.258799999999
    """

    if scale == 0 or value == 0:
        return value

    # Add pow(10.0, -scale - 3) to ensure our smallest digit according to the
    # scale is correct
    return (value * pow(10.0, -scale)) + pow(10.0, -scale - 3)


def string2bin(data, size=None):
    """Convert a string to a byte-string."""

    if isinstance(data, tuple):
        data = data[1]
    datalen = len(data)
    if datalen > size:
        raise j.exceptions.Value("Data %s bigger then size" % repr(data))
    data += "\x00" * (size - datalen)
    return data


def ipaddress2bin(ip_address):
    """Convert an IP address string to a byte-string."""

    out = ""
    for item in ip_address.split("."):
        out += number2bin(int(item), 1)
    return out


def bin2value(data, val_def, check_error_byte=True):
    """Convert a byte-string to the data-type defined in 'val_def'."""

    if data is None:
        raise j.exceptions.Value("Invalid data")
    if check_error_byte:
        errorcode = bin2int(data[:1])
        data = data[1:]
        if errorcode != 0:
            return errorcode, None
    if val_def.type in ("TYPE_UNSIGNED_NUMBER", "TYPE_TIMESTAMP", "TYPE_COMMAND", "TYPE_EVENTFLAGS"):
        rawnr = bin2int(data)
        number = int2float_ensure_precision(rawnr, val_def.scale)
        return 0, number
    elif val_def.type == "TYPE_SIGNED_NUMBER":
        rawnr = bin2sint(data)
        number = int2float_ensure_precision(rawnr, val_def.scale)
        return 0, number
    elif val_def.type in ("TYPE_UNSIGNED_NUMBER_WITH_TS", "TYPE_SIGNED_NUMBER_WITH_TS"):
        rawnr, timestamp = bin2int_and_stamp(data, val_def)
        number = int2float_ensure_precision(rawnr, val_def.scale)
        return 0, (number, timestamp)
    elif val_def.type == "TYPE_POINTER":
        return 0, bin2int(data)
    elif val_def.type == "TYPE_ENUM":
        return 0, bin2bool(data)
    elif val_def.type == "TYPE_STRING":
        return 0, bin2string(data)
    elif val_def.type in ("TYPE_IP", "TYPE_SUBNETMASK"):
        return 0, bin2ipaddress(data)
    elif val_def.type == "TYPE_MAC":
        return 0, bin2macaddress(data)
    elif val_def.type == "TYPE_VERSION":
        return 0, bin2version(data)
    elif val_def.type == "TYPE_VERSION_FULL":
        return 0, bin2version_full(data)
    elif val_def.type == "TYPE_RAW":  # Do nothing
        return 0, data
    else:
        raise Exception("Unknown data type " + val_def.type)


def values2bin(data, val_def):
    """
    Return the bin value of all converted values and the count of the items.
    """

    if isinstance(data, (list, set, tuple)):
        total = ""
        for value in data:
            total += value2bin(value, val_def)
        return total, len(data)
    else:
        return value2bin(data, val_def), 1


def value2bin(data, val_def):
    """Convert data with its type defined in 'val_def' to a byte-string."""

    if data is None:
        raise j.exceptions.Value("Invalid data")
    # valdef represent the return of a get call, setting will be differeot for NumberWithTs types
    #    if val_def.type.endswith("NUMBER_WITH_TS"):
    #        val_def.size = 2
    if val_def.type in ("TYPE_UNSIGNED_NUMBER", "TYPE_TIMESTAMP", "TYPE_COMMAND", "TYPE_EVENTFLAGS"):
        number = float2int_ensure_precision(data, val_def.scale)
        return int2bin(number, val_def.size, False)
    elif val_def.type in ("TYPE_UNSIGNED_NUMBER_WITH_TS", "TYPE_SIGNED_NUMBER_WITH_TS"):
        number = float2int_ensure_precision(data, val_def.scale)
        signed = val_def.type.startswith("TYPE_SIGNED_NUMBER")
        return int2bin(number, val_def.size - 4, signed)
    elif val_def.type.startswith("TYPE_SIGNED_NUMBER"):
        number = float2int_ensure_precision(data, val_def.scale)
        return int2bin(number, val_def.size, True)
    elif val_def.type == "TYPE_ENUM":
        return int2bin(data, 1, False)
    elif val_def.type == "TYPE_STRING":
        return string2bin(data, val_def.length)
    elif val_def.type in ("TYPE_IP", "TYPE_SUBNETMASK"):
        return ipaddress2bin(data)
    elif val_def.type == "TYPE_MAC":
        parts = data.split(":")
        if len(parts) != 6:
            raise j.exceptions.RuntimeError("Invalid mac format '%s'" % data)
        out = ""
        for part in parts:
            out += int2bin(int(part, 16), 1, False)

        return out
    elif val_def.type == "TYPE_RAW":  # Do nothing
        return data.ljust(val_def.size, "\x00")
    elif val_def.type == "TYPE_VERSION":
        parts = str(data).split(".")
        major = parts[0]
        minor = parts[1] if len(parts) == 2 else "0"
        out = int2bin(int(major), 1, False)
        out += int2bin(int(minor), 1, False)
        return out
    else:
        raise Exception("Unknown data type " + val_def.type)


def bin2version(data):
    """Convert a byte-string to a short-version string (major.minor)."""

    major = bin2int(data[0])
    minor = bin2int(data[1])
    return float("%d.%d" % (major, minor))


def bin2version_full(data):
    """Convert a byte-string to a long-version string (major.minor.build.revision)."""

    major = bin2int(data[0])
    minor = bin2int(data[1])
    build = bin2int(data[2])
    revision = bin2int(data[3])
    return "%d.%d.%d.%d" % (major, minor, build, revision)


def bin2bool(data):
    """Convert a byte-string to a boolean."""

    return bool(bin2int(data))


def bin2string(data):
    """Convert a byte-string to a unicode string."""

    idx = data.find(b"\x00")
    if idx != -1:
        data = data[:idx]
    return data.decode("utf-8")


def bin2ipaddress(data):
    """Convert a byte-string to an IP address."""

    chunks = list()
    for chunk in data:
        chunks.append(bin2int(chunk))
    return ".".join((str(x) for x in chunks))


def bin2macaddress(data):
    """Convert a byte-string to a MAC address."""

    mac = binascii.b2a_hex(data)
    chunks = list()
    for i in range(len(mac)):
        if i % 2 == 0:
            chunks.append(mac[i : i + 2])

    result = b":".join(chunks)
    return result.decode()


def bin2int(data):
    """Convert a byte-string to an integer."""

    number = 0
    if isinstance(data, int):  # A single byte is given
        number += data
    else:
        for idx, byte in enumerate(data):
            number += byte * (256 ** idx)
    return number


def int2bin(value, size, signed):
    """Convert an integer to a byte-string."""

    types = {1: "b", 2: "h", 4: "i", 8: "q"}
    if size not in types:
        raise j.exceptions.Value("Invalid size")
    _type = types[size]
    if not signed:
        _type = _type.upper()
    data = struct.pack(">%s" % _type, value)
    result = ""
    for char in data:
        result = chr(char) + result
    return result


def bin2sint(data):
    """Convert a byte-string to a signed integer."""

    number = 0
    # convert binary bytes into digits
    arr = list()
    for byte in data:
        arr.append(byte)
    byteslen = len(data)
    # Now do the processing
    negative = False
    if arr[byteslen - 1] >= 128:
        negative = True
    for idx, byte in enumerate(arr):
        if negative:
            byte = byte ^ 0xFF
        number += byte * (256 ** idx)
    if negative:
        number = (number + 1) * -1
    return number


def number2bin(number, size):
    """Convert a number to a byte-string."""

    # If the number is > than maxSize, number = maxSize
    if number > 2 ** (8 * size):
        number = (2 ** (8 * size)) - 1
    strval = hex(number)[2:]
    diff = size * 2 - len(strval)
    if diff > 0:
        strval = ("0" * diff) + strval
    newval = ""
    for i in range(len(strval)):
        if i % 2 == 0:
            newval = strval[i : i + 2] + newval
    return binascii.a2b_hex(newval)


def bin2int_and_stamp(data, val_def):
    """Convert a byte-string to a tuple containing an integer and a timestamp."""

    numsize = val_def.size - 4
    num = data[0:numsize]
    stamp = data[numsize:]
    if val_def.type == "TYPE_SIGNED_NUMBER_WITH_TS":
        num = bin2sint(num)
    else:
        num = bin2int(num)

    return num, bin2int(stamp)


# split string into array of strings, each len(string) <= length
def slice_string(data, length=None):
    """Split a string into an array of strings, each len(string) <= length."""

    i = 0
    result = []
    datalen = len(data)
    while i * length < datalen:
        item = data[i * length : (i + 1) * length]
        result.append(item)
        i += 1
    return result


def pointer2values(data, params_info):
    """Convert the result of the powerPointer-data to a dict of values."""

    data_types = {
        "bool": 1,
        "TYPE_IP": 4,
        "TYPE_SUBNETMASK": 4,
        "TYPE_MAC": 6,
        "TYPE_TIMESTAMP": 4,
        "TYPE_VERSION": 2,
        "TYPE_STRING": "length",
        "TYPE_UNSIGNED_NUMBER": "size",
        "TYPE_SIGNED_NUMBER": "size",
        "TYPE_UNSIGNED_NUMBER_WITH_TS": "size",
        "TYPE_SIGNED_NUMBER_WITH_TS": "size",
        "TYPE_RAW": "size",
        "TYPE_POINTER": 2,
        "TYPE_ENUM": "size",
        "TYPE_COMMAND": "size",
    }
    # Get the error code
    # errorCode = bin2int(data[0])
    # if errorCode:
    #    return errorCode,None
    # Initialize variables
    val_list = []
    i = 0

    for _, val_def, count in params_info:  # guid not needed in
        size = 0
        if val_def.type in data_types:
            # Get the size from the dictionary
            size = data_types[val_def.type]
            # If size is not constant, get the attribute value
            if isinstance(size, str):
                size = getattr(val_def, size)

            ports = slice_string(data[i : i + (size * count)], size)
            for j in range(0, count):
                ports[j] = bin2value(ports[j], val_def, False)[1]
            i += size * count
            port_count = len(ports)
            if port_count == 0:
                raise Exception("zero ports, xml error?")
            elif port_count == 1:
                val_list.append(ports[0])
            else:
                val_list.append(ports)
        else:
            raise Exception("Unknown data type " + repr(val_def.type))
    return val_list
