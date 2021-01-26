from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value

from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Master(BaseModule):
    def __init__(self, parent):
        super(Master, self).__init__(parent)

        self._pointerGuids = [(1, 1), (2, 1), (3, 1), (11, 1), (14, 1), (17, 1), (18, 1), (20, 1), (5006, 1), (5007, 1)]

        self._guidTable.update(
            {
                1: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                2: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                3: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),
                4: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                5: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='Hz'\nscale=3"),
                6: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                7: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                8: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                9: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                10: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kVAh'\nscale=3"),
                11: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                12: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                13: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='rpm'\nscale=0"),
                14: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                15: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='VA'\nscale=0"),
                16: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
                17: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                18: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                19: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='VA'\nscale=0"),
                20: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                21: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kVAh'\nscale=3"),
                22: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
                23: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='m/s'\nscale=1"),
                24: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='s'\nscale=0"),
                31: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                5000: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
                5001: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
                5002: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
                5003: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
                5004: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                5005: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                5006: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
                5007: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
                5008: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='%RH'\nscale=1"),
                5009: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='%RH'\nscale=1"),
                5010: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
                5011: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
                5012: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
                5013: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
                5014: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
                5015: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
                5016: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
                5017: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
                10000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                10002: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10003: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10004: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                10005: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                10006: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                10007: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                10010: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10011: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10012: Value("type='TYPE_SUBNETMASK'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10013: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10014: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10015: Value("type='TYPE_MAC'\nsize=6\nlength=6\nunit=''\nscale=0"),
                10016: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10017: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10018: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10019: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10020: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10021: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                10022: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10023: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10024: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10025: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                10026: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                10027: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10028: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10029: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10030: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='s'\nscale=0"),
                10031: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10032: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='min'\nscale=0"),
                10033: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10034: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10035: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10036: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='1H8L'\nscale=0"),
                10037: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='s'\nscale=0"),
                10038: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                10039: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                10040: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                10041: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                10042: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                10043: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                10044: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                10045: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                10046: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                10047: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                10048: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                10049: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                10050: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kWh'\nscale=3"),
                10051: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kVAh'\nscale=3"),
                10052: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                10053: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                10054: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                10055: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                10056: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10057: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10058: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10059: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10060: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10061: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10062: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10063: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=1"),
                10064: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
                10065: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
                10066: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='s'\nscale=0"),
                10067: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10068: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10069: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10070: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10071: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kWh'\nscale=3"),
                10072: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kVAh'\nscale=3"),
                10099: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='s'\nscale=0"),
                40000: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40002: Value("type='TYPE_COMMAND'\nsize=16\nlength=16\nunit=''\nscale=0"),
                40003: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40004: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40005: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40006: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40007: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40008: Value("type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),
                40009: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40010: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40011: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40012: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                40013: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40014: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40015: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50000: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50001: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50002: Value("type='TYPE_CIRCULAR_BUFFER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50003: Value("type='TYPE_CIRCULAR_BUFFER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50004: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50005: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50006: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50007: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50008: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50009: Value("type='TYPE_RAW'\nsize=2\nlength=2\nunit=''\nscale=0"),
                50010: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50011: Value("type='TYPE_RAW'\nsize=16\nlength=16\nunit=''\nscale=0"),
                60000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                60001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                60002: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                60004: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                60005: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                60010: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                60020: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                60021: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
            }
        )

    # Attribute 'CurrentTime' GUID  3 Data type TYPE_TIMESTAMP
    # Unix timestamp of the current time
    def getCurrentTime(self):
        guid = 3
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentTime(self, value):
        guid = 3
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Temperature' GUID  11 Data type TYPE_SIGNED_NUMBER
    # Temperature
    def getTemperature(self):
        guid = 11
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getMinTemperature(self):
        guid = 5006
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxTemperature' GUID  5007 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Maximum temperature occurred since last reset
    def getMaxTemperature(self):
        guid = 5007
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'AdminLogin' GUID 10067 Data type TYPE_STRING
    def getUDPUser(self):
        guid = 40013
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'UDPUser' GUID  40013 Data type TYPE_COMMAND
    # User mode for UDP commands
    def setUDPUser(self, value):
        guid = 40013
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Address' GUID  10000 Data type TYPE_UNSIGNED_NUMBER
    # Identification of the module
    def getAddress(self, portnumber=1, length=1):
        guid = 10000
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModuleName' GUID  10001 Data type TYPE_STRING
    # Module name
    def getModuleName(self, moduleID="M1"):
        guid = 10001
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION
    # Firmware version
    def getFirmwareVersion(self, moduleID="M1"):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION
    # Hardware version
    def getHardwareVersion(self, moduleID="M1"):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareID' GUID  10004 Data type TYPE_STRING
    # Identification of the firmware
    def getFirmwareID(self, moduleID="M1"):
        guid = 10004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareID' GUID  10005 Data type TYPE_STRING
    # Identification of the hardware
    def getHardwareID(self, moduleID="M1"):
        guid = 10005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'RackName' GUID  10006 Data type TYPE_STRING
    # Rack Name
    def getRackName(self):
        guid = 10006
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setRackName(self, value):
        guid = 10006
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'RackPosition' GUID  10007 Data type TYPE_STRING
    # Position of the PDU in the rack
    def getRackPosition(self):
        guid = 10007
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setRackPosition(self, value):
        guid = 10007
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DoHotReset' GUID  40014 Data type TYPE_COMMAND
    # Hot reset of the device
    def doHotReset(self):
        guid = 40014
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'TemperatureUnitSelector' GUID  10010 Data type TYPE_ENUM
    def getTemperatureUnitSelector(self):
        guid = 10010
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureUnitSelector(self, value):
        guid = 10010
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'IPAddress' GUID  10011 Data type TYPE_IP
    # IP-address
    def getIPAddress(self):
        guid = 10011
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setIPAddress(self, value):
        guid = 10011
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SubNetMask' GUID  10012 Data type TYPE_SUBNETMASK
    # Subnetmask
    def getSubNetMask(self):
        guid = 10012
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSubNetMask(self, value):
        guid = 10012
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'StdGateWay' GUID  10013 Data type TYPE_IP
    # Standard gateway IP
    def getStdGateWay(self):
        guid = 10013
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setStdGateWay(self, value):
        guid = 10013
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DnsServer' GUID  10014 Data type TYPE_IP
    # Dns server IP
    def getDnsServer(self):
        guid = 10014
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDnsServer(self, value):
        guid = 10014
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MAC' GUID  10015 Data type TYPE_MAC
    # MAC address
    def getMAC(self):
        guid = 10015
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'DHCPEnable' GUID  10016 Data type TYPE_ENUM
    # DHCP enable
    def getDHCPEnable(self):
        guid = 10016
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDHCPEnable(self, value):
        guid = 10016
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'NTPServer' GUID  10017 Data type TYPE_IP
    # NTP server IP
    def getNTPServer(self):
        guid = 10017
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setNTPServer(self, value):
        guid = 10017
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'UseDefaultNTPServer' GUID  10018 Data type TYPE_ENUM
    def getUseDefaultNTPServer(self):
        guid = 10018
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setUseDefaultNTPServer(self, value):
        guid = 10018
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'UseNTP' GUID  10019 Data type TYPE_ENUM
    def setUseNTP(self, value):
        guid = 10019
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPTrapRecvIP' GUID  10020 Data type TYPE_IP
    # SNMP trap server IP-address
    def getSNMPTrapRecvIP(self):
        guid = 10020
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvIP(self, value):
        guid = 10020
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPTrapRecvPort' GUID  10021 Data type TYPE_UNSIGNED_NUMBER
    def getSNMPTrapRecvPort(self):
        guid = 10021
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvPort(self, value):
        guid = 10021
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPCommunityRead' GUID  10022 Data type TYPE_STRING
    def getSNMPCommunityRead(self):
        guid = 10022
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPCommunityRead(self, value):
        guid = 10022
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPCommunityWrite' GUID  10023 Data type TYPE_STRING
    def getSNMPCommunityWrite(self):
        guid = 10023
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPCommunityWrite(self, value):
        guid = 10023
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPControl' GUID  10024 Data type TYPE_ENUM
    def getSNMPControl(self):
        guid = 10024
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPControl(self, value):
        guid = 10024
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'LDAPServer' GUID  10028 Data type TYPE_IP
    def getLDAPServer(self):
        guid = 10028
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setLDAPServer(self, value):
        guid = 10028
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'UseLDAPServer' GUID  10029 Data type TYPE_ENUM
    def doUseLDAPServer(self):
        guid = 10029
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Beeper' GUID  10030 Data type TYPE_UNSIGNED_NUMBER
    # Beeper control enable beeper for n seconds
    def getBeeper(self):
        guid = 10030
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setBeeper(self, value):
        guid = 10030
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DisplayLock' GUID  10031 Data type TYPE_ENUM
    def getDisplayLock(self):
        guid = 10031
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDisplayLock(self, value):
        guid = 10031
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DisplayTimeOn' GUID  10032 Data type TYPE_UNSIGNED_NUMBER
    def getDisplayTimeOn(self):
        guid = 10032
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDisplayTimeOn(self, value):
        guid = 10032
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DisplayRotation' GUID  10033 Data type TYPE_ENUM
    def getDisplayRotation(self):
        guid = 10033
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDisplayRotation(self, value):
        guid = 10033
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinTemperatureWarning' GUID  10052 Data type
    # TYPE_SIGNED_NUMBER
    def getMinTemperatureWarning(self):
        guid = 10052
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, value):
        guid = 10052
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTemperatureWarning' GUID  10053 Data type
    # TYPE_SIGNED_NUMBER
    def getMaxTemperatureWarning(self):
        guid = 10053
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, value):
        guid = 10053
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Startuptime' GUID  10066 Data type TYPE_UNSIGNED_NUMBER
    def getStartuptime(self):
        guid = 10066
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'JumpBoot' GUID  40000 Data type TYPE_COMMAND
    # Enter bootloader mode. Normally this command is only sent to application program. When the bootloader
    # is already running, this command will only reply a positive acknowledge.
    def doJumpBoot(self):
        guid = 40000
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'GotoFactoryMode' GUID  40002 Data type TYPE_COMMAND
    def doGotoFactoryMode(self):
        guid = 40002
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ModNum' GUID  40007 Data type TYPE_UNSIGNED_NUMBER
    # To retrieve the number of modules connected to the device. The device
    # itself is treated as module 0.
    def getModNum(self):
        guid = 40007
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, portnumber=1, length=1):
        guid = 40008
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ApplyIPSettings' GUID  40009 Data type TYPE_COMMAND
    def doApplyIPSettings(self):
        guid = 40009
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DHCPReset' GUID  40010 Data type TYPE_COMMAND
    # Reset DHCP
    def doDHCPReset(self):
        guid = 40010
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'CurrentIP' GUID  14 Data type TYPE_IP
    # Gives the current IP. When DHCP is on, you can see here what ip is given
    # by the DHCP server
    def getCurrentIP(self):
        guid = 14
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalCurrent' GUID  17 Data type TYPE_UNSIGNED_NUMBER
    # Total current
    def getTotalCurrent(self):
        guid = 17
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalRealPower' GUID  18 Data type TYPE_UNSIGNED_NUMBER
    # Total real power
    def getTotalRealPower(self):
        guid = 18
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalActiveEnergy' GUID  20 Data type TYPE_UNSIGNED_NUMBER
    # Total active energy
    def getTotalActiveEnergy(self):
        guid = 20
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MonitorAutoRefresh' GUID  50010 Data type TYPE_POINTER
    # Get the monitor values from the module that are auto refreshed
    def getMonitorAutoRefresh(self):
        guid = 50010
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Role' GUID  40011 Data type TYPE_ENUM
    # To see in which role you are logged in
    def getRole(self):
        guid = 40011
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setUserLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 1
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\0")  # pylint: disable=W1401
        password = password.ljust(16, "\0")  # pylint: disable=W1401
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setRestrictedLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 2
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\0")  # pylint: disable=W1401
        password = password.ljust(16, "\0")  # pylint: disable=W1401
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setAdminLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 3
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\0")  # pylint: disable=W1401
        password = password.ljust(16, "\0")  # pylint: disable=W1401
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # The pointer
    def getMasterPointer(self):
        moduleID = "M1"
        return self._getPointerData(moduleID)


class Power(BaseModule):
    def __init__(self, parent):
        super(Power, self).__init__(parent)

        self._pointerGuids = [
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 8),
            (7, 8),
            (8, 8),
            (9, 8),
            (10, 8),
            (11, 1),
            (24, 1),
            (5000, 8),
            (5001, 8),
            (5002, 1),
            (5003, 1),
            (5004, 1),
            (5005, 1),
            (5006, 1),
            (5007, 1),
            (5010, 8),
            (5011, 8),
            (5012, 8),
            (5013, 8),
            (5014, 1),
            (5015, 1),
            (5016, 1),
            (5017, 1),
            (15, 8),
            (16, 8),
            (17, 1),
            (18, 1),
            (19, 1),
            (20, 1),
            (21, 1),
            (22, 1),
        ]

        self._guidTable = {
            1: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            2: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            3: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),
            4: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
            5: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='Hz'\nscale=3"),
            6: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            7: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            8: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            9: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
            10: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kVAh'\nscale=3"),
            11: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
            12: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
            13: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='rpm'\nscale=0"),
            14: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            15: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='VA'\nscale=0"),
            16: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
            17: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            18: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            19: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='VA'\nscale=0"),
            20: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
            21: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kVAh'\nscale=3"),
            22: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
            23: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='m/s'\nscale=1"),
            24: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='s'\nscale=0"),
            31: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            5000: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
            5001: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
            5002: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
            5003: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
            5004: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
            5005: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
            5006: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
            5007: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
            5008: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='%RH'\nscale=1"),
            5009: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='%RH'\nscale=1"),
            5010: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
            5011: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
            5012: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
            5013: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
            5014: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=3"),
            5015: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='W'\nscale=0"),
            5016: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
            5017: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=5\nlength=5\nunit='%'\nscale=0"),
            10000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
            10002: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10003: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10004: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
            10005: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
            10006: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
            10007: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
            10010: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10011: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10012: Value("type='TYPE_SUBNETMASK'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10013: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10014: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10015: Value("type='TYPE_MAC'\nsize=6\nlength=6\nunit=''\nscale=0"),
            10016: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10017: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10018: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10019: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10020: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10021: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            10022: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10023: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10024: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10025: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            10026: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            10027: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10028: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10029: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10030: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='s'\nscale=0"),
            10031: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10032: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='min'\nscale=0"),
            10033: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10034: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10035: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10036: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='1H8L'\nscale=0"),
            10037: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='s'\nscale=0"),
            10038: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            10039: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            10040: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            10041: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            10042: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            10043: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
            10044: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            10045: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
            10046: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
            10047: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
            10048: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
            10049: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
            10050: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kWh'\nscale=3"),
            10051: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kVAh'\nscale=3"),
            10052: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
            10053: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
            10054: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
            10055: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
            10056: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10057: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10058: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10059: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10060: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10061: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
            10062: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            10063: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=1"),
            10064: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
            10065: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0"),
            10066: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='s'\nscale=0"),
            10067: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10068: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10069: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10070: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
            10071: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kWh'\nscale=3"),
            10072: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=8\nlength=8\nunit='kVAh'\nscale=3"),
            10099: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='s'\nscale=0"),
            40000: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40002: Value("type='TYPE_COMMAND'\nsize=16\nlength=16\nunit=''\nscale=0"),
            40003: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40004: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40005: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40006: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40007: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40008: Value("type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),
            40009: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40010: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40011: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40012: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
            40013: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40014: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            40015: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50000: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50001: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50002: Value("type='TYPE_CIRCULAR_BUFFER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50003: Value("type='TYPE_CIRCULAR_BUFFER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50004: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50005: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50006: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50007: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50008: Value("type='TYPE_RAW'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50009: Value("type='TYPE_RAW'\nsize=2\nlength=2\nunit=''\nscale=0"),
            50010: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            50011: Value("type='TYPE_RAW'\nsize=16\nlength=16\nunit=''\nscale=0"),
            60000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            60001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            60002: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            60004: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            60005: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
            60010: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
            60020: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
            60021: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
        }

    # Attribute 'CurrentTime' GUID  3 Data type TYPE_TIMESTAMP
    # Unix timestamp of the current time
    def getCurrentTime(self, moduleID):
        guid = 3
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Voltage' GUID  4 Data type TYPE_UNSIGNED_NUMBER
    # True RMS Voltage
    def getVoltage(self, moduleID):
        guid = 4
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Frequency' GUID  5 Data type TYPE_UNSIGNED_NUMBER
    # Frequency
    def getFrequency(self, moduleID):
        guid = 5
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Current' GUID  6 Data type TYPE_UNSIGNED_NUMBER
    # Current true RMS
    def getCurrent(self, moduleID, portnumber=1, length=1):
        guid = 6
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Power' GUID  7 Data type TYPE_UNSIGNED_NUMBER
    # Real Power
    def getPower(self, moduleID, portnumber=1, length=1):
        guid = 7
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'StatePortCur' GUID  8 Data type TYPE_ENUM
    # current port state
    def getStatePortCur(self, moduleID, portnumber=1, length=1):
        guid = 8
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ActiveEnergy' GUID  9 Data type TYPE_UNSIGNED_NUMBER
    # Active Energy
    def getActiveEnergy(self, moduleID, portnumber=1, length=1):
        guid = 9
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ApparentEnergy' GUID  10 Data type TYPE_UNSIGNED_NUMBER
    # Apparent Energy
    def getApparentEnergy(self, moduleID, portnumber=1, length=1):
        guid = 10
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Temperature' GUID  11 Data type TYPE_SIGNED_NUMBER
    # Temperature
    def getTemperature(self, moduleID):
        guid = 11
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxCurrent' GUID  5000 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum port current occurred since last reset
    def getMaxCurrent(self, moduleID, portnumber=1, length=1):
        guid = 5000
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxCurrent(self, moduleID, portnumber=1):
        guid = 5000
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxPower' GUID  5001 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum port power occurred since last reset
    def getMaxPower(self, moduleID, portnumber=1, length=1):
        guid = 5001
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxPower(self, moduleID, portnumber=1):
        guid = 5001
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxTotalCurrent' GUID  5002 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total current occurred since last reset
    def getMaxTotalCurrent(self, moduleID):
        guid = 5002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTotalCurrent(self, moduleID):
        guid = 5002
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxTotalPower' GUID  5003 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total power occurred since last reset
    def getMaxTotalPower(self, moduleID):
        guid = 5003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTotalPower(self, moduleID):
        guid = 5003
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxVoltage' GUID  5004 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum voltage occurred since last reset
    def getMaxVoltage(self, moduleID):
        guid = 5004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxVoltage(self, moduleID):
        guid = 5004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinVoltage' GUID  5005 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum voltage occurred since last reset
    def getMinVoltage(self, moduleID):
        guid = 5005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMinVoltage(self, moduleID):
        guid = 5005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTemperature' GUID  5006 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Minimum temperature occurred since last reset
    def getMinTemperature(self, moduleID):
        guid = 5006
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMinTemperature(self, moduleID):
        guid = 5006
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxTemperature' GUID  5007 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Maximum temperature occurred since last reset
    def getMaxTemperature(self, moduleID):
        guid = 5007
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTemperature(self, moduleID):
        guid = 5007
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Address' GUID  10000 Data type TYPE_UNSIGNED_NUMBER
    # Identification of the module
    def getAddress(self, moduleID, portnumber=1, length=1):
        guid = 10000
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModuleName' GUID  10001 Data type TYPE_STRING
    # Module name
    def getModuleName(self, moduleID):
        guid = 10001
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setModuleName(self, moduleID, value):
        guid = 10001
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION
    # Firmware version
    def getFirmwareVersion(self, moduleID):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION
    # Hardware version
    def getHardwareVersion(self, moduleID):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareID' GUID  10004 Data type TYPE_STRING
    # Identification of the firmware
    def getFirmwareID(self, moduleID):
        guid = 10004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareID' GUID  10005 Data type TYPE_STRING
    # Identification of the hardware
    def getHardwareID(self, moduleID):
        guid = 10005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TemperatureUnitSelector' GUID  10010 Data type TYPE_ENUM
    def getTemperatureUnitSelector(self, moduleID):
        guid = 10010
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureUnitSelector(self, moduleID, value):
        guid = 10010
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'PortName' GUID  10034 Data type TYPE_STRING
    # Name of the port
    def getPortName(self, moduleID, portnumber=1, length=1):
        guid = 10034
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPortName(self, moduleID, value, portnumber=1):
        guid = 10034
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'PortState' GUID  10035 Data type TYPE_ENUM
    # The state of the port, only used to set the port state, see current port
    # state to get the port state
    def setPortState(self, moduleID, value, portnumber=1):
        guid = 10035
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'CurrentPriorOff' GUID  10036 Data type TYPE_UNSIGNED_NUMBER
    # Priority level switch off when maximum total current exceeds threshold
    def getCurrentPriorOff(self, moduleID, portnumber=1, length=1):
        guid = 10036
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentPriorOff(self, moduleID, value, portnumber=1):
        guid = 10036
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DelayOn' GUID  10037 Data type TYPE_UNSIGNED_NUMBER
    # Port activation delay after power recycle
    def getDelayOn(self, moduleID, portnumber=1, length=1):
        guid = 10037
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDelayOn(self, moduleID, value, portnumber=1):
        guid = 10037
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxCurrentOff' GUID  10038 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current switch off level
    def getMaxCurrentOff(self, moduleID, portnumber=1, length=1):
        guid = 10038
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxCurrentOff(self, moduleID, value, portnumber=1):
        guid = 10038
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxCurrentWarning' GUID  10039 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMaxCurrentWarning(self, moduleID, portnumber=1, length=1):
        guid = 10039
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxCurrentWarning(self, moduleID, value, portnumber=1):
        guid = 10039
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxPowerOff' GUID  10040 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port power switch off level
    def getMaxPowerOff(self, moduleID, portnumber=1, length=1):
        guid = 10040
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxPowerOff(self, moduleID, value, portnumber=1):
        guid = 10040
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxPowerWarning' GUID  10041 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port power warning level
    def getMaxPowerWarning(self, moduleID, portnumber=1, length=1):
        guid = 10041
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxPowerWarning(self, moduleID, value, portnumber=1):
        guid = 10041
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalCurrentOff' GUID  10042 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total current switch off level
    def getMaxTotalCurrentOff(self, moduleID):
        guid = 10042
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalCurrentOff(self, moduleID, value):
        guid = 10042
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalCurrentWarning' GUID  10043 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total current warning level
    def getMaxTotalCurrentWarning(self, moduleID):
        guid = 10043
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalCurrentWarning(self, moduleID, value):
        guid = 10043
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalPowerOff' GUID  10044 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total power switch off level
    def getMaxTotalPowerOff(self, moduleID):
        guid = 10044
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalPowerOff(self, moduleID, value):
        guid = 10044
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalPowerWarning' GUID  10045 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total power warning level
    def getMaxTotalPowerWarning(self, moduleID):
        guid = 10045
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalPowerWarning(self, moduleID, value):
        guid = 10045
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxVoltageOff' GUID  10046 Data type TYPE_UNSIGNED_NUMBER
    # Maximum voltage switch off level
    def getMaxVoltageOff(self, moduleID):
        guid = 10046
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageOff(self, moduleID, value):
        guid = 10046
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxVoltageWarning' GUID  10047 Data type TYPE_UNSIGNED_NUMBER
    # Maximum voltage warning level
    def getMaxVoltageWarning(self, moduleID):
        guid = 10047
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageWarning(self, moduleID, value):
        guid = 10047
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinVoltageOff' GUID  10048 Data type TYPE_UNSIGNED_NUMBER
    # Minimum voltage switch off level
    def getMinVoltageOff(self, moduleID):
        guid = 10048
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageOff(self, moduleID, value):
        guid = 10048
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinVoltageWarning' GUID  10049 Data type TYPE_UNSIGNED_NUMBER
    # Minimum voltage warning level
    def getMinVoltageWarning(self, moduleID):
        guid = 10049
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageWarning(self, moduleID, value):
        guid = 10049
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ActiveEnergyReset' GUID  10050 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Active Energy
    def doActiveEnergyReset(self, moduleID):
        guid = 10050
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef))
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentEnergyReset' GUID  10051 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Apparent Energy
    def doApparentEnergyReset(self, moduleID, portnumber=1):
        guid = 10051
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinTemperatureWarning' GUID  10052 Data type
    # TYPE_SIGNED_NUMBER
    def getMinTemperatureWarning(self, moduleID):
        guid = 10052
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, moduleID, value):
        guid = 10052
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTemperatureWarning' GUID  10053 Data type
    # TYPE_SIGNED_NUMBER
    def getMaxTemperatureWarning(self, moduleID):
        guid = 10053
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, moduleID, value):
        guid = 10053
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Startuptime' GUID  10066 Data type TYPE_UNSIGNED_NUMBER
    def getStartuptime(self, moduleID):
        guid = 10066
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'PowerCycleTime' GUID  10099 Data type TYPE_UNSIGNED_NUMBER
    # The time that power will be switched off when power cycle is started
    def getPowerCycleTime(self, moduleID, portnumber=1, length=1):
        guid = 10099
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPowerCycleTime(self, moduleID, value, portnumber=1):
        guid = 10099
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'JumpBoot' GUID  40000 Data type TYPE_COMMAND
    # Enter bootloader mode. Normally this command is only sent to application program. When the bootloader
    # is already running, this command will only reply a positive acknowledge.
    def getJumpBoot(self, moduleID):
        guid = 40000
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setJumpBoot(self, moduleID, value):
        guid = 40000
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'GotoFactoryMode' GUID  40002 Data type TYPE_COMMAND
    def setGotoFactoryMode(self, moduleID, value):
        guid = 40002
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentPower' GUID  15 Data type TYPE_UNSIGNED_NUMBER
    # Apparent power (this is the product of the current and the voltage)
    def getApparentPower(self, moduleID, portnumber=1, length=1):
        guid = 15
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, moduleID):
        guid = 40008
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'PowerFactor' GUID  16 Data type TYPE_UNSIGNED_NUMBER
    # Powerfactor
    def getPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 16
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinCurrent' GUID  5010 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port current occurred since last reset
    def getMinCurrent(self, moduleID, portnumber=1, length=1):
        guid = 5010
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinPower' GUID  5011 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port power occured since last reset
    def getMinPower(self, moduleID, portnumber=1, length=1):
        guid = 5011
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinPowerFactor' GUID  5012 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum powerfactor occured per port since last reset
    def getMinPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 5012
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxPowerFactor' GUID  5013 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum powerfactor occured per port since last reset
    def getMaxPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 5013
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'BootJumpApp' GUID  60001 Data type TYPE_COMMAND
    # Jump to the application, which starts at 0x4000.
    def setBootJumpApp(self, moduleID, value):
        guid = 60001
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'TotalCurrent' GUID  17 Data type TYPE_UNSIGNED_NUMBER
    # Total current
    def getTotalCurrent(self, moduleID):
        guid = 17
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalRealPower' GUID  18 Data type TYPE_UNSIGNED_NUMBER
    # Total real power
    def getTotalRealPower(self, moduleID):
        guid = 18
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalApparentPower' GUID  19 Data type TYPE_UNSIGNED_NUMBER
    # Total apparent power
    def getTotalApparentPower(self, moduleID):
        guid = 19
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalActiveEnergy' GUID  20 Data type TYPE_UNSIGNED_NUMBER
    # Total active energy
    def getTotalActiveEnergy(self, moduleID):
        guid = 20
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalApparentEnergy' GUID  21 Data type TYPE_UNSIGNED_NUMBER
    # Total apparent energy
    def getTotalApparentEnergy(self, moduleID):
        guid = 21
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalPowerFactor' GUID  22 Data type TYPE_UNSIGNED_NUMBER
    # Total power factor
    def getTotalPowerFactor(self, moduleID):
        guid = 22
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalCurrent' GUID  5014 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port current occurred since last reset
    def getMinTotalCurrent(self, moduleID):
        guid = 5014
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalPower' GUID  5015 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port power occurred since last reset
    def getMinTotalPower(self, moduleID):
        guid = 5015
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalPowerFactor' GUID  5016 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum total power factor occurred since last reset
    def getMinTotalPowerFactor(self, moduleID):
        guid = 5016
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxTotalPowerFactor' GUID  5017 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total power factor occurred since last reset
    def getMaxTotalPowerFactor(self, moduleID):
        guid = 5017
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ActiveTotalEnergyReset' GUID  10071 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Active Total Energy / time of reset + value at that time
    def doActiveTotalEnergyReset(self, moduleID):
        guid = 10071
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentTotalEnergyReset' GUID  10072 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Apparent Total Energy / time of reset + value at that time
    def doApparentTotalEnergyReset(self, moduleID):
        guid = 10072
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MonitorAutoRefresh' GUID  50010 Data type TYPE_POINTER
    # Get the monitor values from the module that are auto refreshed
    def getMonitorAutoRefresh(self, moduleID):
        guid = 50010
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'DoHotReset' GUID  40014 Data type TYPE_COMMAND
    # Hot reset of the device
    def doHotReset(self, moduleID):
        guid = 40014
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # The pointer
    def getPowerPointer(self, moduleID):
        return self._getPointerData(moduleID)

    def getPower(self, moduleID):
        powerPointers = self.getPowerPointer(moduleID)
        pointerMeaning = {
            1: "GeneralModuleStatus",
            2: "SpecificModuleStatus",
            3: "CurrentTime",
            4: "Voltage",
            5: "Frequency",
            6: "Current",
            7: "Power",
            8: "StatePortCur",
            9: "ActiveEnergy",
            10: "ApparentEnergy",
            11: "Temperature",
            15: "ApparentPower",
            16: "PowerFactor",
            17: "TotalCurrent",
            18: "TotalRealPower",
            19: "TotalApparentPower",
            20: "TotalActiveEnergy",
            21: "TotalApparentEnergy",
            22: "TotalPowerFactor",
            24: "TimeOnline",
            5000: "MaxCurrent",
            5001: "MaxPower",
            5002: "MaxTotalCurrent",
            5003: "MaxTotalPower",
            5004: "MaxVoltage",
            5005: "MinVoltage",
            5006: "MinTemperature",
            5007: "MaxTemperature",
            5010: "MinCurrent",
            5011: "MinPower",
            5012: "MinPowerFactor",
            5013: "MaxPowerFactor",
            5014: "MinTotalCurrent",
            5015: "MinTotalPower",
            5016: "MinTotalPowerFactor",
            5017: "MaxTotalPowerFactor",
        }
        result = dict()
        for key, value in powerPointers.items():
            result[pointerMeaning[key]] = value

        return result
