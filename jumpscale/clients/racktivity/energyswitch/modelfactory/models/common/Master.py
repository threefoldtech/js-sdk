from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Master(BaseModule):
    def __init__(self, parent):
        super(Master, self).__init__(parent)
        self._guidTable.update(
            {
                # ModuleName
                10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # TemperatureWarningEvent
                10087: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

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

    # The pointer
    def getMasterPointer(self):
        moduleID = "M1"
        return self._getPointerData(moduleID)

    # TemperatureWarningEvent
    def getTemperatureWarningEvent(self):
        guid = 10087
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureWarningEvent(self, value):
        guid = 10087
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
