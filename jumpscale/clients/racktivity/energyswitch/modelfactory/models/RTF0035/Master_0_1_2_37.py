from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value

from jumpscale.clients.racktivity.energyswitch.modelfactory.models.RTF0035.Master_0_1_2_21 import Model as Master


class Model(Master):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self._guidTable.update(
            {
                # TransducerSelection
                10189: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # GenericTransducerParameters
                10190: Value("type='TYPE_SIGNED_NUMBER'\nsize=4\nlength=4\nunit='mA/V'\nscale=0"),
                # RezeroTransducer
                40050: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

        self._pointerGuids = [
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 2),
            (11, 1),
            (14, 1),
            (34, 1),
            (35, 1),
            (36, 1),
            (41, 12),
            (43, 12),
            (44, 2),
            (45, 2),
            (46, 12),
            (47, 12),
            (48, 2),
            (49, 2),
            (5004, 2),
            (5005, 2),
            (5006, 1),
            (5007, 1),
            (5024, 12),
            (5025, 12),
            (5026, 12),
            (5027, 12),
            (5028, 2),
            (5029, 2),
            (5030, 2),
            (5031, 2),
        ]

    def getTransducerSelection(self, portnumber):
        moduleID = "M1"
        guid = 10189
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTransducerSelection(self, value, portnumber):
        guid = 10189
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getGenericTransducerParameters(self, portnumber):
        moduleID = "M1"
        guid = 10190
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setGenericTransducerParameters(self, value, portnumber):
        guid = 10190
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def rezeroTransducer(self, portnumber):
        guid = 40050
        moduleID = "M1"
        value = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
