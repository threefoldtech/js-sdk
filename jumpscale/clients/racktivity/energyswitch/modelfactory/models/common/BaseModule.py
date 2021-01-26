from jumpscale.clients.racktivity.energyswitch.common import convert


class BaseModule:
    def __init__(self, parent):
        self._parent = parent
        self._guidTable = {}
        self._pointerGuids = []

    def definePointerStructure(self):
        """prepares definition of binary structure

        @param guidList - list of tuples (guid, count)
        @param guidDef - dictionary of guid -> definition

        returns paramInfo structure - list of tuples (guid, definition, count)
        """
        paramInfo = []

        for (guid, length) in self._pointerGuids:
            paramInfo.append((guid, self._guidTable[guid], length))

        return paramInfo

    def _getPointerData(self, moduleID):
        """private function to get pointer data from device and convert to dict

        """
        paramInfo = self.definePointerStructure()

        data = self._parent.client.getPointer(moduleID)
        array = convert.pointer2values(data, paramInfo)
        result = dict()
        for idx, info in enumerate(paramInfo):
            result[info[0]] = array[idx]
        return result
