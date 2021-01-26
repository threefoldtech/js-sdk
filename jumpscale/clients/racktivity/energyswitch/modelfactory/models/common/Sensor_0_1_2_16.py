from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from copy import copy
from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.Sensor import Sensor


class Model(Sensor):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._guidTable.update(
            {
                # CurrentTime
                3: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),
                # Voltage
                4: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # Temperature
                11: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # Humidity
                12: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                # DewPoint
                25: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='K'\nscale=1"),
                # AnalogIn
                27: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # MotionDetected
                29: Value("type='TYPE_ENUM'\nsize=2\nlength=2\nunit=''\nscale=1"),
                # HighCurrent
                41: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # HighPower
                43: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=1"),
                # MaxVoltage
                5004: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                # MinVoltage
                5005: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                # MinHighCurrent
                5024: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MaxHighCurrent
                5025: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MinHighPower
                5026: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=1"),
                # MaxHighPower
                5027: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=1"),
                # Module Address
                10000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # Module Name
                10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # FirmwareVersion
                10002: Value("type='TYPE_VERSION_FULL'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # HardwareVersion
                10003: Value("type='TYPE_VERSION_FULL'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # FirmwareID
                10004: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # HardwareID
                10005: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # TempUnitSelector
                10010: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # MinAnalogInputWarn
                10111: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # MaxAnalogInputWarn
                10112: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # MaxVoltageWarning
                10047: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # MinVoltageWarning
                10049: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # MinTemperatureWarning
                10052: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # MaxTemperatureWarning
                10053: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # MinHumidityWarn
                10054: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                # MaxHumidityWarn
                10055: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='%RH'\nscale=1"),
                # ExternalSensorLabel
                10109: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # MaxHighCurrentWarning
                10165: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # MinHighCurrentWarning
                10176: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # MaxHighPowerWarning
                10177: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=1"),
                # MinHighPowerWarning
                10178: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=1"),
                # CmdLocate
                40028: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleCapabilities
                40030: Value("type='TYPE_COMMAND'\nsize=2\nlength=2\nunit=''\nscale=0"),
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
    # Voltage
    def getVoltage(self, moduleID):
        guid = 4
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Temperature' GUID  11 Data type TYPE_SIGNED_NUMBER
    # Temperature
    def getTemperature(self, moduleID, portnumber=1, length=1):
        guid = 11
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        if len(data) < 3 or (ord(data[1]) == 255 and ord(data[2]) == 255):
            # The sensor is not connected
            return 1, None

        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Humidity' GUID  12 Data type TYPE_UNSIGNED_NUMBER
    # Humidity
    def getHumidity(self, moduleID):
        guid = 12
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Dewpoint' GUID  12 Data type TYPE_UNSIGNED_NUMBER
    # Dewpoint
    def getDewpoint(self, moduleID):
        guid = 25
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'Analog Input' GUID  12 Data type TYPE_UNSIGNED_NUMBER
    # AnalogInput
    def getAnalogInput(self, moduleID, portnumber=1, length=1):
        guid = 27
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HighCurrent' GUID  41 Data type TYPE_SIGNED_NUMBER
    # Current for high voltages
    def getHighCurrent(self, moduleID):
        guid = 41
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HighPower' GUID  43 Data type TYPE_SIGNED_NUMBER
    # Power for high voltages
    def getHighPower(self, moduleID):
        guid = 43
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxVoltage' GUID  5004 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Maximum Voltage
    def getMaxVoltage(self, moduleID):
        guid = 5004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinVoltage' GUID  5005 Data type TYPE_UNSIGNED_NUMBER_WITH_TS
    # Minimum Voltage
    def getMinVoltage(self, moduleID):
        guid = 5005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinVoltage' GUID  5024 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Minimum Current for high voltages
    def getMinHighCurrent(self, moduleID):
        guid = 5024
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxVoltage' GUID  5025 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Maximum Current for high voltages
    def getMaxHighCurrent(self, moduleID):
        guid = 5025
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MinVoltage' GUID  5026 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Minimum Power for high voltages
    def getMinHighPower(self, moduleID):
        guid = 5026
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxVoltage' GUID  5027 Data type TYPE_SIGNED_NUMBER_WITH_TS
    # Maximum Power for high voltages
    def getMaxHighPower(self, moduleID):
        guid = 5027
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
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

    # Attribute 'MaxVoltageWarning' GUID  10047 Data type TYPE_UNSIGNED_NUMBER
    # Maximum Voltage Warning
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

    # Attribute 'MinVoltageWarning' GUID  10049 Data type TYPE_UNSIGNED_NUMBER
    # Minimum Voltage Warning
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

    # Attribute 'ExternalSensorLabel' GUID  10109 Data type TYPE_STRING
    # External Sensor Label
    def getExternalSensorLabel(self, moduleID, portnumber=1):
        guid = 10109
        valDef = self._guidTable[guid]
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setExternalSensorLabel(self, moduleID, value, portnumber=1):
        guid = 10109
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxHighCurrentWarning' GUID  10165 Data type TYPE_SIGNED_NUMBER
    # Maximum Current for high voltages Warning
    def getMaxHighCurrentWarning(self, moduleID):
        guid = 10165
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxHighCurrentWarning(self, moduleID, value):
        guid = 10165
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinHighCurrentWarning' GUID  10176 Data type TYPE_SIGNED_NUMBER
    # Maximum Current for high voltages Warning
    def getMinHighCurrentWarning(self, moduleID):
        guid = 10176
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinHighCurrentWarning(self, moduleID, value):
        guid = 10176
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxHighPowerWarning' GUID  10177 Data type TYPE_SIGNED_NUMBER
    # Maximum Power for high voltages Warning
    def getMaxHighPowerWarning(self, moduleID):
        guid = 10177
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxHighPowerWarning(self, moduleID, value):
        guid = 10177
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinHighPowerWarning' GUID  10178 Data type TYPE_SIGNED_NUMBER
    # Maximum Power for high voltages Warning
    def getMinHighPowerWarning(self, moduleID):
        guid = 10178
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinHighPowerWarning(self, moduleID, value):
        guid = 10178
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ModuleCapabilities' GUID  40030 Data type TYPE_COMMAND
    # Module Capabilities
    def getModuleCapabilities(self, moduleID):
        guid = 40030
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'MaxHumidityWarning' GUID  10055 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMaxHumidityWarning(self, moduleID):
        guid = 10055
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxHumidityWarning(self, moduleID, value):
        guid = 10055
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinHumidityWarning' GUID  10054 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMinHumidityWarning(self, moduleID):
        guid = 10054
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinHumidityWarning(self, moduleID, value):
        guid = 10054
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxTemperatureWarning' GUID  10053 Data type TYPE_SIGNED_NUMBER
    # Maximum port current warning level
    def getMaxTemperatureWarning(self, moduleID, portnumber=1):
        guid = 10053
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, moduleID, value, portnumber=1):
        guid = 10053
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'getMinTemperatureWarning' GUID  10052 Data type TYPE_SIGNED_NUMBER
    # Maximum port current warning level
    def getMinTemperatureWarning(self, moduleID, portnumber=1):
        guid = 10052
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, moduleID, value, portnumber=1):
        guid = 10052
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MaxAnalogueInputWarning' GUID  10112 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMaxAnalogueInputWarning(self, moduleID):
        guid = 10112
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxAnalogueInputWarning(self, moduleID, value):
        guid = 10112
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'MinAnalogueInputWarning' GUID  10111 Data type TYPE_UNSIGNED_NUMBER
    # Maximum port current warning level
    def getMinAnalogueInputWarning(self, moduleID):
        guid = 10111
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinAnalogueInputWarning(self, moduleID, value):
        guid = 10111
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # locate EnergySensor command
    def getCmdLocate(self, moduleID):
        guid = 40028
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCmdLocate(self, moduleID, value):
        guid = 40028
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
