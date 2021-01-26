from copy import copy

from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value

from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Model(BaseModule):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                # Temperature
                11: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # ModuleName
                10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # FirmwareVersion
                10002: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # HardwareVersion
                10003: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # FirmwareID
                10004: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # HardwareID
                10005: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # SNMPTrapRecvIP
                10020: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # SNMPTrapRecvPort
                10021: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # MinTemperatureWarning
                10052: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # MaxTemperatureWarning
                10053: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # GeneralEventEnable
                10074: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # TemperatureWarningEvent
                10087: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModInfo
                40008: Value("type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),
                # LoginAndPassword
                40012: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # ModStatus
                40018: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleManagement
                40026: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleScan
                40027: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

    # Temperature
    def getTemperature(self):
        guid = 11
        moduleID = "M1"
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

    def getModuleName(self):
        guid = 10001
        portnumber = 0
        length = 1
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setModuleName(self, value):
        guid = 10001
        portnumber = 0
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

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

    # Attribute 'SNMPTrapRecvIP' GUID  10020 Data type TYPE_IP
    # SNMP trap server IP-address
    def getSNMPTrapRecvIP(self, portnumber):
        guid = 10020
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvIP(self, value, portnumber):
        guid = 10020
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'SNMPTrapRecvPort' GUID  10021 Data type TYPE_UNSIGNED_NUMBER
    def getSNMPTrapRecvPort(self, portnumber=1):
        guid = 10021
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvPort(self, value, portnumber=1):
        guid = 10021
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinTemperatureWarning' GUID  10052 Data type
    # TYPE_SIGNED_NUMBER
    def getMinTemperatureWarning(self):
        moduleID = "M1"
        guid = 10052
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, value):
        moduleID = "M1"
        guid = 10052
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTemperatureWarning' GUID  10053 Data type
    # TYPE_SIGNED_NUMBER
    def getMaxTemperatureWarning(self):
        moduleID = "M1"
        guid = 10053
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, value):
        moduleID = "M1"
        guid = 10053
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

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

    # TemperatureWarningEvent
    def getTemperatureWarningEvent(self):
        moduleID = "M1"
        guid = 10087
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureWarningEvent(self, value):
        moduleID = "M1"
        guid = 10087
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, portnumber=1, length=1):
        guid = 40008
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setUserLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 1
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\x00")
        password = password.ljust(16, "\x00")
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setRestrictedLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 2
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\x00")
        password = password.ljust(16, "\x00")
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setAdminLoginAndPassword(self, name, password):
        guid = 40012
        moduleID = "M1"
        portnumber = 3
        valDef = self._guidTable[guid]
        name = name.ljust(16, "\x00")
        password = password.ljust(16, "\x00")
        value = name + password
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
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
