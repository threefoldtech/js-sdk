from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Master_0_0_4_20 import Model as Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                # DeviceID
                10150: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # DeviceVersion
                10151: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # HeartbeatInterval
                10179: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='kW'\nscale=0"),
                # SlaveCapabilities
                40036: Value("type='TYPE_COMMAND'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # SlaveVersions
                40037: Value("type='TYPE_COMMAND'\nsize=4\nlength=4\nunit=''\nscale=0"),
            }
        )

    # Attribute 'HeartbeatInterval' GUID  10179 Data type TYPE_UNSIGNED_NUMBER
    # Heartbeat Interval
    def getHeartbeatInterval(self):
        guid = 10179
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, 0)
        return self._parent.getObjectFromData(data, valDef)

    def setHeartbeatInterval(self, value):
        guid = 10179
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), 0)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getSlaveCapabilities(self, portnumber=1, length=32):
        guid = 40036
        moduleID = "M1"
        # portnumber = 1
        # length = 32
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getSlaveVersions(self, portnumber=1, length=32):
        guid = 40037
        moduleID = "M1"
        # portnumber = 1
        # length = 32
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)
