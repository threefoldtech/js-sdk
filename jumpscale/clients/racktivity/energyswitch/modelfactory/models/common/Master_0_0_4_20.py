from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Master_0_0_4_4 import Model as Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                37: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                38: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                39: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=2\nunit='min'\nscale=0"),
                40: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=2\nunit='%'\nscale=1"),
                # SNMP Trap Community String
                10073: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                10156: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                10157: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                10158: Value("type='TYPE_STRING'\nsize=64\nlength=64\nunit=''\nscale=0"),
                10159: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%'\nscale=1"),
                10160: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%'\nscale=1"),
            }
        )

    # UPSPresent
    def getUPSPresent(self):
        moduleID = "M1"
        guid = 37
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # UPSStatus
    def getUPSStatus(self):
        moduleID = "M1"
        guid = 38
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # UPSEstimatedRunTime
    def getUPSEstimatedRunTime(self):
        moduleID = "M1"
        guid = 39
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # UPSBatteryLevel
    def getUPSBatteryLevel(self):
        moduleID = "M1"
        guid = 40
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    def getSNMPTrapCommunityRead(self):
        guid = 10073
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapCommunityRead(self, value):
        guid = 10073
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # SSOIPAddress
    def setSSOIPAddress(self, ip):
        moduleID = "M1"
        guid = 10156
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(ip, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getSSOIPAddress(self):
        moduleID = "M1"
        guid = 10156
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # SSOLoginCredentials
    def setSSOLoginCredentials(self, credentials):
        moduleID = "M1"
        guid = 10157
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(credentials, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # SSOGracefullShutdown
    def setSSOGracefullShutdown(self, url):
        moduleID = "M1"
        guid = 10158
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(url, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getSSOGracefullShutdown(self):
        moduleID = "M1"
        guid = 10158
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # UPSWarningLevel
    def setUPSWarningLevel(self, level):
        moduleID = "M1"
        guid = 10159
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(level, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getUPSWarningLevel(self):
        moduleID = "M1"
        guid = 10159
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    # UPSOffLevel
    def setUPSOffLevel(self, level):
        moduleID = "M1"
        guid = 10160
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(level, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getUPSOffLevel(self):
        moduleID = "M1"
        guid = 10160
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)
