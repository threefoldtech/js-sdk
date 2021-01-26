from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.common import calculate
from copy import copy
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Power_0_0_5_4 import Model as Power
import struct
import time


class Model(Power):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                50013: Value("type='TYPE_RAW'\nsize=0\nlength=0\nunit=''\nscale=0"),
                50014: Value("type='TYPE_RAW'\nsize=0\nlength=0\nunit=''\nscale=0"),
            }
        )

    # Attribute 'CurrentTime' GUID  3 Data type TYPE_TIMESTAMP
    # Unix timestamp of the current time
    def getCurrentTime(self, moduleID):
        guid = 3
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Voltage' GUID  4 Data type TYPE_UNSIGNED_NUMBER
    # True RMS Voltage
    def getVoltage(self, moduleID):
        guid = 4
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Frequency' GUID  5 Data type TYPE_UNSIGNED_NUMBER
    # Frequency
    def getFrequency(self, moduleID):
        guid = 5
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Current' GUID  6 Data type TYPE_UNSIGNED_NUMBER
    # Current true RMS
    def getCurrent(self, moduleID, portnumber=1, length=1):
        guid = 6
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Power' GUID  7 Data type TYPE_UNSIGNED_NUMBER
    # Real Power
    def getPortPower(self, moduleID, portnumber=1, length=1):
        guid = 7
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPower(self, moduleID):
        powerPointers = self.getPowerPointer(moduleID)
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
            31: "Unknown(Not to be used)",
            50: "Unknown(Not to be used)",
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

    # Attribute 'StatePortCur' GUID  8 Data type TYPE_ENUM
    # current port state
    def getStatePortCur(self, moduleID, portnumber=1, length=1):
        guid = 8
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ActiveEnergy' GUID  9 Data type TYPE_UNSIGNED_NUMBER
    # Active Energy
    def getActiveEnergy(self, moduleID, portnumber=1, length=1):
        guid = 9
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ApparentEnergy' GUID  10 Data type TYPE_UNSIGNED_NUMBER
    # Apparent Energy
    def getApparentEnergy(self, moduleID, portnumber=1, length=1):
        guid = 10
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Temperature' GUID  11 Data type TYPE_SIGNED_NUMBER
    # Temperature
    def getTemperature(self, moduleID):
        guid = 11
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxCurrent' GUID  5000 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum port current occurred since last reset
    def getMaxCurrent(self, moduleID, portnumber=1, length=1):
        guid = 5000
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxCurrent(self, moduleID, portnumber=1):
        guid = 5000
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxPower' GUID  5001 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum port power occurred since last reset
    def getMaxPower(self, moduleID, portnumber=1, length=1):
        guid = 5001
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxPower(self, moduleID, portnumber=1):
        guid = 5001
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxTotalCurrent' GUID  5002 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total current occurred since last reset
    def getMaxTotalCurrent(self, moduleID):
        guid = 5002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTotalCurrent(self, moduleID):
        guid = 5002
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxTotalPower' GUID  5003 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total power occurred since last reset
    def getMaxTotalPower(self, moduleID):
        guid = 5003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTotalPower(self, moduleID):
        guid = 5003
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=1)

    # Attribute 'MaxVoltage' GUID  5004 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum voltage occurred since last reset
    def getMaxVoltage(self, moduleID):
        guid = 5004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxVoltage(self, moduleID):
        guid = 5004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinVoltage' GUID  5005 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum voltage occurred since last reset
    def getMinVoltage(self, moduleID):
        guid = 5005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMinVoltage(self, moduleID):
        guid = 5005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTemperature' GUID  5006 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Minimum temperature occurred since last reset
    def getMinTemperature(self, moduleID):
        guid = 5006
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMinTemperature(self, moduleID):
        guid = 5006
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxTemperature' GUID  5007 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Maximum temperature occurred since last reset
    def getMaxTemperature(self, moduleID):
        guid = 5007
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def resetMaxTemperature(self, moduleID):
        guid = 5007
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.resetAttribute(moduleID, guid, portnumber)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Address' GUID  10000 Data type TYPE_UNSIGNED_NUMBER
    # Identification of the module
    def getAddress(self, moduleID, portnumber=1, length=1):
        guid = 10000
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModuleName' GUID  10001 Data type TYPE_STRING
    # Module name
    def getModuleName(self, moduleID):
        guid = 10001
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setModuleName(self, moduleID, value):
        guid = 10001
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION
    # Firmware version
    def getFirmwareVersion(self, moduleID):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareVersion' GUID  10002 Data type TYPE_VERSION_FULL
    # Firmware version
    # Return the firmware version as a string (example: '1.2.0.6')
    def getFirmwareVersionStr(self, moduleID):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION
    # Hardware version
    def getHardwareVersion(self, moduleID):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION_FULL
    # Hardware version
    # Return the hardware version as a string (example: '1.2.0.6')
    def getHardwareVersionStr(self, moduleID):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareID' GUID  10004 Data type TYPE_STRING
    # Identification of the firmware
    def getFirmwareID(self, moduleID):
        guid = 10004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareID' GUID  10005 Data type TYPE_STRING
    # Identification of the hardware
    def getHardwareID(self, moduleID):
        guid = 10005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TemperatureUnitSelector' GUID  10010 Data type TYPE_ENUM
    def getTemperatureUnitSelector(self, moduleID):
        guid = 10010
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureUnitSelector(self, moduleID, value):
        guid = 10010
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'PortName' GUID  10034 Data type TYPE_STRING
    # Name of the port
    def getPortName(self, moduleID, portnumber=1, length=1):
        guid = 10034
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPortName(self, moduleID, value, portnumber=1):
        guid = 10034
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'PortState' GUID  10035 Data type TYPE_ENUM
    # The state of the port, only used to set the port state, see current port
    # state to get the port state
    def setPortState(self, moduleID, value, portnumber=1):
        guid = 10035
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'CurrentPriorOff' GUID  10036 Data type TYPE_UNSIGNED_NUMBER
    # Priority level switch off when maximum total current exceeds threshold
    def getCurrentPriorOff(self, moduleID, portnumber=1, length=1):
        guid = 10036
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentPriorOff(self, moduleID, value, portnumber=1):
        guid = 10036
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'DelayOn' GUID  10037 Data type TYPE_UNSIGNED_NUMBER
    # Port activation delay after power recycle
    def getDelayOn(self, moduleID, portnumber=1, length=1):
        guid = 10037
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setDelayOn(self, moduleID, value, portnumber=1):
        guid = 10037
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxCurrentOff' GUID  10038 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current switch off level
    def getMaxCurrentOff(self, moduleID, portnumber=1, length=1):
        guid = 10038
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxCurrentOff(self, moduleID, value, portnumber=1):
        guid = 10038
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxCurrentWarning' GUID  10039 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMaxCurrentWarning(self, moduleID, portnumber=1, length=1):
        guid = 10039
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxCurrentWarning(self, moduleID, value, portnumber=1):
        guid = 10039
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxPowerOff' GUID  10040 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port power switch off level
    def getMaxPowerOff(self, moduleID, portnumber=1, length=1):
        guid = 10040
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxPowerOff(self, moduleID, value, portnumber=1):
        guid = 10040
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxPowerWarning' GUID  10041 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port power warning level
    def getMaxPowerWarning(self, moduleID, portnumber=1, length=1):
        guid = 10041
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxPowerWarning(self, moduleID, value, portnumber=1):
        guid = 10041
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalCurrentOff' GUID  10042 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total current switch off level
    def getMaxTotalCurrentOff(self, moduleID):
        guid = 10042
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalCurrentOff(self, moduleID, value):
        guid = 10042
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalCurrentWarning' GUID  10043 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total current warning level
    def getMaxTotalCurrentWarning(self, moduleID):
        guid = 10043
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalCurrentWarning(self, moduleID, value):
        guid = 10043
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalPowerOff' GUID  10044 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total power switch off level
    def getMaxTotalPowerOff(self, moduleID):
        guid = 10044
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalPowerOff(self, moduleID, value):
        guid = 10044
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTotalPowerWarning' GUID  10045 Data type TYPE_UNSIGNED_NUMBER
    # Maximum total power warning level
    def getMaxTotalPowerWarning(self, moduleID):
        guid = 10045
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTotalPowerWarning(self, moduleID, value):
        guid = 10045
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxVoltageOff' GUID  10046 Data type TYPE_UNSIGNED_NUMBER
    # Maximum voltage switch off level
    def getMaxVoltageOff(self, moduleID):
        guid = 10046
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageOff(self, moduleID, value):
        guid = 10046
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxVoltageWarning' GUID  10047 Data type TYPE_UNSIGNED_NUMBER
    # Maximum voltage warning level
    def getMaxVoltageWarning(self, moduleID):
        guid = 10047
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageWarning(self, moduleID, value):
        guid = 10047
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinVoltageOff' GUID  10048 Data type TYPE_UNSIGNED_NUMBER
    # Minimum voltage switch off level
    def getMinVoltageOff(self, moduleID):
        guid = 10048
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageOff(self, moduleID, value):
        guid = 10048
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinVoltageWarning' GUID  10049 Data type TYPE_UNSIGNED_NUMBER
    # Minimum voltage warning level
    def getMinVoltageWarning(self, moduleID):
        guid = 10049
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageWarning(self, moduleID, value):
        guid = 10049
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ActiveEnergyReset' GUID  10050 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Active Energy
    def doActiveEnergyReset(self, moduleID):
        guid = 10050
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef))
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentEnergyReset' GUID  10051 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Apparent Energy
    def doApparentEnergyReset(self, moduleID, portnumber=1):
        guid = 10051
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinTemperatureWarning' GUID  10052 Data type
    # TYPE_SIGNED_NUMBER
    def getMinTemperatureWarning(self, moduleID):
        guid = 10052
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, moduleID, value):
        guid = 10052
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTemperatureWarning' GUID  10053 Data type
    # TYPE_SIGNED_NUMBER
    def getMaxTemperatureWarning(self, moduleID):
        guid = 10053
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, moduleID, value):
        guid = 10053
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'Startuptime' GUID  10066 Data type TYPE_UNSIGNED_NUMBER
    def getStartuptime(self, moduleID):
        guid = 10066
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'PowerCycleTime' GUID  10099 Data type TYPE_UNSIGNED_NUMBER
    # The time that power will be switched off when power cycle is started
    def getPowerCycleTime(self, moduleID, portnumber=1, length=1):
        guid = 10099
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPowerCycleTime(self, moduleID, value, portnumber=1):
        guid = 10099
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'JumpBoot' GUID  40000 Data type TYPE_COMMAND
    # Enter bootloader mode. Normally this command is only sent to application
    # program. When the bootloader is already running, this command will only
    # reply a positive acknowledge.
    def getJumpBoot(self, moduleID):
        guid = 40000
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setJumpBoot(self, moduleID, value):
        guid = 40000
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'GotoFactoryMode' GUID  40002 Data type TYPE_COMMAND
    def setGotoFactoryMode(self, moduleID, value):
        guid = 40002
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentPower' GUID  15 Data type TYPE_UNSIGNED_NUMBER
    # Apparent power (this is the product of the current and the voltage)
    def getApparentPower(self, moduleID, portnumber=1, length=1):
        guid = 15
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, moduleID):
        guid = 40008
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'PowerFactor' GUID  16 Data type TYPE_UNSIGNED_NUMBER
    # Powerfactor
    def getPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 16
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinCurrent' GUID  5010 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port current occurred since last reset
    def getMinCurrent(self, moduleID, portnumber=1, length=1):
        guid = 5010
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinPower' GUID  5011 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port power occured since last reset
    def getMinPower(self, moduleID, portnumber=1, length=1):
        guid = 5011
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinPowerFactor' GUID  5012 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum powerfactor occured per port since last reset
    def getMinPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 5012
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxPowerFactor' GUID  5013 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum powerfactor occured per port since last reset
    def getMaxPowerFactor(self, moduleID, portnumber=1, length=1):
        guid = 5013
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'BootJumpApp' GUID  60001 Data type TYPE_COMMAND
    # Jump to the application, which starts at 0x4000.
    def setBootJumpApp(self, moduleID, value):
        guid = 60001
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'TotalCurrent' GUID  17 Data type TYPE_UNSIGNED_NUMBER
    # Total current
    def getTotalCurrent(self, moduleID):
        guid = 17
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalRealPower' GUID  18 Data type TYPE_UNSIGNED_NUMBER
    # Total real power
    def getTotalRealPower(self, moduleID):
        guid = 18
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalApparentPower' GUID  19 Data type TYPE_UNSIGNED_NUMBER
    # Total apparent power
    def getTotalApparentPower(self, moduleID):
        guid = 19
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalActiveEnergy' GUID  20 Data type TYPE_UNSIGNED_NUMBER
    # Total active energy
    def getTotalActiveEnergy(self, moduleID):
        guid = 20
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalApparentEnergy' GUID  21 Data type TYPE_UNSIGNED_NUMBER
    # Total apparent energy
    def getTotalApparentEnergy(self, moduleID):
        guid = 21
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'TotalPowerFactor' GUID  22 Data type TYPE_UNSIGNED_NUMBER
    # Total power factor
    def getTotalPowerFactor(self, moduleID):
        guid = 22
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalCurrent' GUID  5014 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port current occurred since last reset
    def getMinTotalCurrent(self, moduleID):
        guid = 5014
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalPower' GUID  5015 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum port power occurred since last reset
    def getMinTotalPower(self, moduleID):
        guid = 5015
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinTotalPowerFactor' GUID  5016 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum total power factor occurred since last reset
    def getMinTotalPowerFactor(self, moduleID):
        guid = 5016
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxTotalPowerFactor' GUID  5017 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum total power factor occurred since last reset
    def getMaxTotalPowerFactor(self, moduleID):
        guid = 5017
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'ActiveTotalEnergyReset' GUID  10071 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Active Total Energy / time of reset + value at that time
    def doActiveTotalEnergyReset(self, moduleID):
        guid = 10071
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ApparentTotalEnergyReset' GUID  10072 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Apparent Total Energy / time of reset + value at that time
    def doApparentTotalEnergyReset(self, moduleID):
        guid = 10072
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MonitorAutoRefresh' GUID  50010 Data type TYPE_POINTER
    # Get the monitor values from the module that are auto refreshed
    def getMonitorAutoRefresh(self, moduleID):
        guid = 50010
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'DoHotReset' GUID  40014 Data type TYPE_COMMAND
    # Hot reset of the device
    def doHotReset(self, moduleID):
        guid = 40014
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(1, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setOscilloscopeTimeSample(self, moduleID, portnumber):
        guid = 40004
        value = portnumber * 16 + 8
        valDef = self._guidTable[guid]
        data = self._parent.client.setData(moduleID, guid, data=convert.value2bin(value, valDef), length=1)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def setOscilloscopeFrequencySample(self, moduleID, portnumber):
        guid = 40005
        value = portnumber * 16 + 8
        valDef = self._guidTable[guid]
        data = self._parent.client.setData(moduleID, guid, data=convert.value2bin(value, valDef), length=1)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getOscilloscopeTimeData(self, moduleID, portnumber=1):
        guid = 50013
        result = {"voltage": [], "current": []}

        errorCode = self.setOscilloscopeTimeSample(moduleID=moduleID, portnumber=portnumber)
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
        voltageCalibration = (struct.unpack("<H", rawData[:2]))[0] / 100
        voltageValues = struct.unpack("<256b", rawData[2:258])
        currentCalibration = (struct.unpack("<H", rawData[258:260]))[0]
        currentValues = struct.unpack("<256b", rawData[260:516])

        # Calculate the values based on calibration:
        for i in range(255):
            result["voltage"].append(voltageValues[i] * voltageCalibration / 128)
            result["current"].append(currentValues[i] * currentCalibration / 128)

        return (0, result)

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
        for i in range(0, 256, 4):
            result["voltage"]["amplitudes"].append(
                struct.unpack("<H", voltageSamples[i : i + 2])[0] * voltageCalibration
            )
            result["voltage"]["phases"].append(struct.unpack("<h", voltageSamples[i + 2 : i + 4])[0])
            result["current"]["amplitudes"].append(
                struct.unpack("<H", currentSamples[i : i + 2])[0] * currentCalibration
            )
            result["current"]["phases"].append(struct.unpack("<h", currentSamples[i + 2 : i + 4])[0])

        return (0, result)

    def getTHD(self, moduleID, portnumber=1):
        errorCode, returnedData = self.getOscilloscopeFrequencyData(moduleID, portnumber)
        if errorCode:
            return errorCode, None
        currentHarmonics = returnedData["current"]["amplitudes"]
        return errorCode, calculate.getTHD(currentHarmonics)
