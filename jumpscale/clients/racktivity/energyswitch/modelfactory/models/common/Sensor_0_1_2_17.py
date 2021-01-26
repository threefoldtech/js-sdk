from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value

from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Sensor_0_1_2_16 import Model as Sensor


class Model(Sensor):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                # Sensitivity
                10141: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # MotionWarningEvent
                10149: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # IOPortWarningEvent
                10192: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

    # Attribute 'getMaxSensitivity' GUID  10141 Data type TYPE_UNSIGNED_NUMBER
    # Maximum Sensitivity for high sensitivity Warning
    def getMaxSensitivity(self, moduleID):
        guid = 10141
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'getMaxSensitivity' GUID  10141 Data type TYPE_UNSIGNED_NUMBER
    # Maximum Sensitivity for high sensitivity Warning
    def setMaxSensitivity(self, moduleID, value):
        guid = 10141
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # MotionWarningEvent
    def getMotionWarningEvent(self, moduleID):
        guid = 10149
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMotionWarningEvent(self, moduleID, value):
        guid = 10149
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # IOPortWarningEvent
    def getIOPortWarningEvent(self, moduleID):
        guid = 10192
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setIOPortWarningEvent(self, moduleID, value):
        guid = 10192
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
