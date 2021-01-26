from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Sensor(BaseModule):
    def __init__(self, parent):
        super(Sensor, self).__init__(parent)
        self._guidTable.update(
            {
                # TemperatureWarningEvent
                10087: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # HumidityWarningEvent
                10088: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # DewPointWarningEvent
                10093: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # AnalogueInputWarningEvent
                10116: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

    # TemperatureWarningEvent
    def getTemperatureWarningEvent(self, moduleID, portnumber=1):
        guid = 10087
        portnumber = 1
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureWarningEvent(self, moduleID, value, portnumber=1):
        guid = 10087
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # HumidityWarningEvent
    def getHumidityWarningEvent(self, moduleID):
        guid = 10088
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setHumidityWarningEvent(self, moduleID, value):
        guid = 10088
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # DewPointWarningEvent
    def getDewPointWarningEvent(self, moduleID):
        guid = 10093
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDewPointWarningEvent(self, moduleID, value):
        guid = 10093
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # AnalogueInputWarningEvent
    def getAnalogueInputWarningEvent(self, moduleID, portnumber=1):
        guid = 10116
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setAnalogueInputWarningEvent(self, moduleID, value, portnumber=1):
        guid = 10116
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
