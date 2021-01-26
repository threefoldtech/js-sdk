class Master:
    def __init__(self, parent):
        self._parent = parent
        self._moduleID = "M1"

    def setSNMPTrapRecvIP(self, value, portnumber=0):  # pylint: disable=W0613
        ip = value.split(".")
        return (
            0,
            self._parent.client.setAttribute(
                self._moduleID, "F00624%03d%03d%03d%03d" % (int(ip[0]), int(ip[1]), int(ip[2]), int(ip[3])), ""
            ),
        )

    def getSNMPTrapRecvIP(self, portnumber=0):  # pylint: disable=W0613
        ipaddress = self._parent.client.getAttribute(self._moduleID, "F00624000040000000001")
        return 0, "%d.%d.%d.%d" % (ipaddress[0], ipaddress[1], ipaddress[2], ipaddress[3])


class Power:
    def __init__(self, parent):
        self._parent = parent
        self._moduleID = "P1"

    def getMaxCurrentOff(self, portnumber=1):
        guid = "F%05d000040000000001" % (398 + (portnumber * 2))
        raw = self._parent.client.getAttribute(self._moduleID, guid)
        value = (raw[1] * 256) + ord(raw[0])
        value /= 1000.0
        return 0, value

    def setMaxCurrentOff(self, value, portnumber):
        value = int(value) * 1000
        lastpart = value / 256
        firstpart = value % 256
        guid = "F%05d%03d%03d" % (398 + (portnumber * 2), firstpart, lastpart)
        self._parent.client.setAttribute(self._moduleID, guid)
        return 0

    def getCurrentPriorOff(self, portnumber=1, length=1):
        raw = self._parent.client.getAttribute(self._moduleID, "F00208000080000000001")
        count = 0

        result = []
        for char in raw:
            count += 1
            if count >= portnumber and count < portnumber + length:
                result.append(char)
        return 0, result

    def setCurrentPriorOff(self, value, portnumber):
        guid = "F%05d%03d" % (207 + portnumber, int(value))
        self._parent.client.setAttribute(self._moduleID, guid)
        return 0

    def getStatePortCur(self, portnumber=1, length=1, **kwargs):
        val = ord(self._parent.client.getAttribute(self._moduleID, "F00241000010000000001"))

        result = []
        for i in range(portnumber, portnumber + length):
            result.append(bool(val & 1 << (8 - i)))
        return 0, result

    def setPortState(self, value, portnumber=1, **kwargs):
        if value == 1:  # power on
            val = 1 << (8 - portnumber)
            self._parent.client.resetAttribute(self._moduleID, "OR00146%03d" % val)
        else:  # power off
            val = 256 + ~(1 << (8 - portnumber))
            self._parent.client.resetAttribute(self._moduleID, "AR00146%03d" % val)
        return 0

    def getPowerPointer(self):
        def getValue(raw, size=2):
            value = 0
            for i in range(0, size):
                value += raw[i] * pow(256, i)
            return value

        def convertMeasurement(raw, factor, size=2):
            values = []
            for i in range(0, int(len(raw) / size)):
                value = getValue(raw[i * size :], size) / factor
                values.append(value)
            return values if len(values) > 1 else values[0]

        def convertTemperature(raw):
            return (ord(raw) / 2.0) - 32

        def getPortStatus(raw):
            raw = ord(raw)

            result = []
            for i in range(1, 9):
                result.append(bool(raw & 1 << (8 - i)))
            return result

        def getPower(values):
            # voltage * current
            result = []
            for val in values[6]:
                result.append(values[4] * val)
            return result

        def getPowerFactor(values):
            # power / app power
            result = []
            for i in range(0, len(values[7])):
                val = values[7][i] / float(values[15][i]) if values[15][i] else 0.0
                result.append(val * 100)
            return result

        def getTotalCurrent(values):
            return sum(values[6])

        def getTotalPower(values):
            return sum(values[7])

        def getTotalApparentPower(values):
            return sum(values[15])

        def getTotalActiveEnergy(values):
            return sum(values[9])

        def getTotalApparentEnergy(values):
            return sum(values[10])

        def getTotalPowerFactor(values):
            # total real power / total apparent power
            val = values[18] / values[19] if values[19] else 0.0
            return val * 100

        pointerMap = [
            (1, "GeneralModuleStatus", "R0012300001", ord),
            (2, "SpecificModuleStatus", None),
            (3, "CurrentTime", None),
            (4, "Voltage", "R0009600002", convertMeasurement, 100.0),
            (5, "Frequency", "R0009800002", convertMeasurement, 100.0),
            (6, "Current", "R0006400016", convertMeasurement, 1000.0),
            (7, "Power", "R0008000016", convertMeasurement, 10.0),
            (8, "StatePortCur", "F00241000010000000001", getPortStatus),
            (9, "ActiveEnergy", "R0000000032", convertMeasurement, 1000.0, 4),
            (10, "ApparentEnergy", "R0003200032", convertMeasurement, 1000.0, 4),
            (11, "Temperature", "R0012000001", convertTemperature),
            (15, "ApparentPower", None, getPower),
            (16, "PowerFactor", None, getPowerFactor),
            (17, "TotalCurrent", None, getTotalCurrent),
            (18, "TotalRealPower", None, getTotalPower),
            (19, "TotalApparentPower", None, getTotalApparentPower),
            (20, "TotalActiveEnergy", None, getTotalActiveEnergy),
            (21, "TotalApparentEnergy", None, getTotalApparentEnergy),
            (22, "TotalPowerFactor", None, getTotalPowerFactor),
            (24, "TimeOnline", None),
            (5000, "MaxCurrent", "F00432000160000000001", convertMeasurement, 1000.0),
            (5001, "MaxPower", None),
            (5002, "MaxTotalCurrent", None),
            (5003, "MaxTotalPower", None),
            (5004, "MaxVoltage", None),
            (5005, "MinVoltage", None),
            (5006, "MinTemperature", None),
            (5007, "MaxTemperature", None),
            (5010, "MinCurrent", None),
            (5011, "MinPower", None),
            (5012, "MinPowerFactor", None),
            (5013, "MaxPowerFactor", None),
            (5014, "MinTotalCurrent", None),
            (5015, "MinTotalPower", None),
            (5016, "MinTotalPowerFactor", None),
            (5017, "MaxTotalPowerFactor", None),
        ]

        result = dict()

        # get the initial values
        for pointer in pointerMap:
            if not pointer[2]:
                continue

            value = self._parent.client.getAttribute(self._moduleID, pointer[2])

            # convert if any function is specified
            if len(pointer) > 3:
                args = [value]

                # add args if any
                for i in range(4, len(pointer)):
                    args.append(pointer[i])

                # call conversion function
                value = pointer[3](*args)  # pylint: disable=W0142
            result[pointer[0]] = value

        # set the calculated values
        for pointer in pointerMap:
            if not pointer[2] and len(pointer) > 3 and pointer[3]:
                result[pointer[0]] = pointer[3](result)

        return result

    def getPower(self, **kwargs):
        powerPointers = self.getPowerPointer()
        pointerMeaning = {
            1: "GeneralModuleStatus",
            2: "SpecificModuleStatus",
            3: "CurrentTime",
            4: "Voltage",
            5: "Frequency",
            6: "Current",
            7: "Power",
            8: "StatePortCur",
            9: "ActiveEnergy",
            10: "ApparentEnergy",
            11: "Temperature",
            15: "ApparentPower",
            16: "PowerFactor",
            17: "TotalCurrent",
            18: "TotalRealPower",
            19: "TotalApparentPower",
            20: "TotalActiveEnergy",
            21: "TotalApparentEnergy",
            22: "TotalPowerFactor",
            24: "TimeOnline",
            5000: "MaxCurrent",
            5001: "MaxPower",
            5002: "MaxTotalCurrent",
            5003: "MaxTotalPower",
            5004: "MaxVoltage",
            5005: "MinVoltage",
            5006: "MinTemperature",
            5007: "MaxTemperature",
            5010: "MinCurrent",
            5011: "MinPower",
            5012: "MinPowerFactor",
            5013: "MaxPowerFactor",
            5014: "MinTotalCurrent",
            5015: "MinTotalPower",
            5016: "MinTotalPowerFactor",
            5017: "MaxTotalPowerFactor",
        }
        result = dict()
        for key, value in powerPointers.items():
            result[pointerMeaning[key]] = value

        return result
