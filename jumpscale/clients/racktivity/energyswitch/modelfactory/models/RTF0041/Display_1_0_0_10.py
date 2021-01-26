from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from copy import copy
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Model(BaseModule):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._pointerGuids = []

        self._guidTable.update(
            {
                # GeneralModuleStatus
                1: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # SpecificModuleStatus
                2: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # CurrentTime
                3: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),
                # TimeOnline
                24: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='s'\nscale=0"),
                # LogMeInfo
                31: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # Status
                1000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
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
                # ModInfo
                40008: Value("type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),
            }
        )

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

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION_FULL
    # Firmware version
    # Return the firmware version as a string (example: '1.2.0.6')
    def getFirmwareVersionStr(self, moduleID):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
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

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION_FULL
    # Hardware version
    # Return the hardware version as a string (example: '1.2.0.6')
    def getHardwareVersionStr(self, moduleID):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
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

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, moduleID):
        guid = 40008
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPowerPointer(self, moduleID):
        return self._getPointerData(moduleID)
