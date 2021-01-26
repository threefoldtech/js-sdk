from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Power_0_0_5_17 import Model as Power
import struct
import time


class Model(Power):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update({10161: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='%'\nscale=0")})

    def getOscilloscopeFrequencyData(self, moduleID, portnumber=1):
        guid = 50014
        result = {"current": {"amplitudes": [], "phases": []}, "voltage": {"amplitudes": [], "phases": []}}

        errorCode = self.setOscilloscopeFrequencySample(moduleID=moduleID, portnumber=portnumber)
        if errorCode != 0:
            return (errorCode, None)
        time.sleep(0.5)

        # Get 516 bytes of raw data from device:
        rawData = str()
        for i in range(3):
            raw = self._parent.client.getData(moduleID, guid, index=1 + i * 172, count=172)
            errorCode = struct.unpack("<1B", raw[0])[0]
            if errorCode != 0:
                return (errorCode, None)
            rawData += raw[1:]

        # Extracting values from raw binary data:
        currentCalibration = float((struct.unpack("<H", rawData[:2]))[0]) / 4096
        voltageCalibration = float((struct.unpack("<H", rawData[258:260]))[0]) / 4096
        currentSamples = rawData[2:258]
        voltageSamples = rawData[260:516]
        ok = False
        for i in range(0, 256, 4):
            result["voltage"]["amplitudes"].append(
                struct.unpack("<H", voltageSamples[i : i + 2])[0] * voltageCalibration
            )
            result["voltage"]["phases"].append(struct.unpack("<h", voltageSamples[i + 2 : i + 4])[0])
            result["current"]["phases"].append(struct.unpack("<h", currentSamples[i + 2 : i + 4])[0])

            # Sometimes the current amplitudes returned by the PDU are incorrect
            # Try to check them and return None if so
            currentAmplitude = struct.unpack("<H", currentSamples[i : i + 2])[0]
            if i > 0 and currentAmplitude > 4:
                ok = True
            result["current"]["amplitudes"].append(currentAmplitude * currentCalibration)

        if not ok:
            return (100, None)
        return (0, result)

    # BlockSetPortOff
    def setBlockSetPortOff(self, moduleID, value, portnumber=1):
        guid = 10161
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getBlockSetPortOff(self, moduleID, portnumber=1):
        guid = 10161
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef)
