from copy import copy

from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Master import Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

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
                # GeneralEventEnable
                10074: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
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
                # ModStatus
                40018: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleManagement
                40026: Value("type='TYPE_COMMAND'\nsize=1\nlength=32\nunit=''\nscale=0"),
                # ModuleScan
                40027: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
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

    # Attribute 'Address' GUID  10000 Data type TYPE_UNSIGNED_NUMBER
    # Identification of the module
    def getAddress(self, portnumber=1, length=1):
        guid = 10000
        moduleID = "M1"
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

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION_FULL
    # Firmware version
    # Return the firmware version as a string (example: '1.2.0.6')
    def getFirmwareVersionStr(self, moduleID="M1"):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
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

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION_FULL
    # Hardware version
    # Return the hardware version as a string (example: '1.2.0.6')
    def getHardwareVersionStr(self, moduleID="M1"):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
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
    def getSNMPTrapRecvIP(self, portnumber=0):
        guid = 10020
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvIP(self, value, portnumber=0):
        guid = 10020
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPTrapRecvPort' GUID  10021 Data type TYPE_UNSIGNED_NUMBER
    def getSNMPTrapRecvPort(self, portnumber=0):
        """
        portnumber parameter not used, put only for compatibility
        """
        guid = 10021
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvPort(self, value, portnumber=0):
        """
        portnumber parameter not used, put only for compatibility
        """
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

    # GeneralEventEnable
    def getGeneralEventEnable(self):
        guid = 10074
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setGeneralEventEnable(self, value):
        guid = 10074
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

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

    # Attribute 'DoHotReset' GUID  40014 Data type TYPE_COMMAND
    # Hot reset of the device
    def doHotReset(self):
        guid = 40014
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Returns modules statuses; the data returned can be used to see if the
    # modules are active, present, monitored or managed
    def getModStatus(self):
        guid = 40018
        moduleID = "M1"
        portnumber = 1
        length = 32
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Returns a list with management status of the modules
    # 0 - released, 1- managed
    def getModuleManagement(self):
        guid = 40026
        moduleID = "M1"
        portnumber = 1
        length = 32
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Sets management value for modules
    # 0 - released, 1- managed
    def setModuleManagement(self, value, portnumber=3):
        guid = 40026
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Get  to request status of module scan.
    # (idle = 0, busy = 1, success = 2, fail = 3)
    def getModuleScan(self):
        guid = 40027
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Set to 1 to start a new module scan.
    def setModuleScan(self, value=1):
        guid = 40027
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

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
