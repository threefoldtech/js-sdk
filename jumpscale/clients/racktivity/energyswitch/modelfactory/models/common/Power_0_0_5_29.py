from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Power_0_0_5_20 import Model as Power
import struct
import time


class Model(Power):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self._guidTable.update({50: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%'\nscale=1")})

        self._pointerGuids = [
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 8),
            (7, 8),
            (8, 8),
            (9, 8),
            (10, 8),
            (11, 1),
            (24, 1),
            (31, 8),
            (50, 8),
            (5000, 8),
            (5001, 8),
            (5002, 1),
            (5003, 1),
            (5004, 1),
            (5005, 1),
            (5006, 1),
            (5007, 1),
            (5010, 8),
            (5011, 8),
            (5012, 8),
            (5013, 8),
            (5014, 1),
            (5015, 1),
            (5016, 1),
            (5017, 1),
            (15, 8),
            (16, 8),
            (17, 1),
            (18, 1),
            (19, 1),
            (20, 1),
            (21, 1),
            (22, 1),
        ]

    # Attribute 'THD' GUID 50 Data type TYPE_UNSIGNED_NUMBER
    # Total Harmonic Distortion
    def getTHD(self, moduleID, portnumber=1):
        guid = 50
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getOscilloscopeTimeData(self, moduleID, portnumber=1):
        Ioffset = 258
        result = {"voltage": [], "current": []}

        # Get 516 bytes of raw data from device:
        rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType="T")
        if b"failed" in rawData:
            time.sleep(0.1)
            rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType="T")

        if len(rawData) < 516:
            # something is wrong, not enough data
            return (101, rawData)

        # Extracting values from raw binary data:
        voltageCalibration = float((struct.unpack("<H", rawData[:2]))[0]) / 12800.0
        voltageValues = struct.unpack("<256b", rawData[2:Ioffset])

        # the current values is returned in miliampers
        currentCalibration = float((struct.unpack("<H", rawData[Ioffset : Ioffset + 2]))[0]) / 128.0
        currentValues = struct.unpack("<256b", rawData[Ioffset + 2 : 2 * Ioffset])

        # Calculate the values based on calibration:
        for i in range(256):
            result["voltage"].append(voltageValues[i] * voltageCalibration)
            result["current"].append(currentValues[i] * currentCalibration)

        return (0, result)

    def getOscilloscopeFrequencyData(self, moduleID, portnumber=1, dataType="current"):  # pylint: disable=W0221
        result = {"current": {"amplitudes": [], "phases": []}, "voltage": {"amplitudes": [], "phases": []}}
        dataType = "FC" if dataType == "current" else "FV"
        numSamples = 64

        rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType=dataType)
        if b"failed" in rawData:
            time.sleep(0.1)
            rawData = self._parent.client.getOscData(module=moduleID, outlet=portnumber, dataType=dataType)

        if len(rawData) < 516:
            # something is wrong, not enough data
            return (101, rawData)

        if dataType == "FC":
            # Calculate the values based on calibration:
            currentCalibration = float((struct.unpack("<H", rawData[:2]))[0]) / 4096.0 / 1000
            for i in range(6, 2 + 4 * numSamples, 4):  # do not take DC (0th harmonic)
                currentAmplitude = struct.unpack("<H", rawData[i : i + 2])[0]
                result["current"]["amplitudes"].append(currentAmplitude * currentCalibration)
                # if first harmonic is below 0.01 A it makes no sense to read
                # as on 0 load, there will be useful information
                if len(result["current"]["amplitudes"]) == 1 and result["current"]["amplitudes"][0] < 0.01:
                    return (100, None)
                result["current"]["phases"].append(struct.unpack("<h", rawData[i + 2 : i + 4])[0])
        else:
            length = 256
            VOffset = 2 + length
            voltageCalibration = float((struct.unpack("<H", rawData[VOffset : VOffset + 2]))[0]) * 10 / 4096.0 / 1000
            # Calculate the values based on calibration:
            # do not take DC (0th harmonic)
            for i in range(VOffset + 6, VOffset + 4 * numSamples, 4):
                result["voltage"]["amplitudes"].append(struct.unpack("<H", rawData[i : i + 2])[0] * voltageCalibration)
                result["voltage"]["phases"].append(struct.unpack("<h", rawData[i + 2 : i + 4])[0])
        return (0, result)
