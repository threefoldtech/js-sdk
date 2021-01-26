from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Master_0_1_2_16 import Model as Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self._guidTable.update(
            {
                # ModuleManagement
                40026: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0")
            }
        )

    # Attribute 'SNMPTrapRecvIP' GUID  10020 Data type TYPE_IP
    # SNMP trap server IP-address
    def getSNMPTrapRecvIP(self, portnumber):  # pylint: disable=W0222
        guid = 10020
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvIP(self, value, portnumber):  # pylint: disable=W0222
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

    def setSNMPCommunityRead(self, value):
        guid = 10022
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
