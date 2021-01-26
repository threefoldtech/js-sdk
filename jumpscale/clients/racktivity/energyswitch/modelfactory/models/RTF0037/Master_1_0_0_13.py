from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.RTF0037.Master_0_1_2_41 import Model as Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self._guidTable.update(
            {
                # added only those that are needed for snmp configuration, others
                # omitted
                # SNMPTrapUser
                10212: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # SNMPTrapEnable
                10222: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

    def getSNMPTrapUser(self, portnumber):
        guid = 10212
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapUser(self, value, portnumber):
        guid = 10212
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getSNMPTrapEnable(self, portnumber=1):
        guid = 10222
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapEnable(self, value, portnumber=1):
        guid = 10222
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
