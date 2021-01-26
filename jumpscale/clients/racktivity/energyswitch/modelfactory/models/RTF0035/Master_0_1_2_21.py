from copy import copy

from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value

from jumpscale.clients.racktivity.energyswitch.modelfactory.models.common.BaseModule import BaseModule


class Model(BaseModule):
    def __init__(self, parent):
        super(Model, self).__init__(parent)

        self._pointerGuids = [
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 2),
            (11, 1),
            (14, 1),
            (17, 2),
            (18, 1),
            (34, 1),
            (35, 1),
            (36, 1),
            (41, 12),
            (42, 1),
            (43, 12),
            (44, 2),
            (45, 2),
            (46, 12),
            (47, 12),
            (48, 2),
            (49, 2),
            (5006, 1),
            (5007, 1),
            (5026, 12),
            (5027, 12),
            (5028, 2),
            (5029, 2),
            (5030, 2),
            (5031, 2),
            (5004, 2),
            (5005, 2),
            (5024, 12),
            (5025, 12),
        ]

        self._guidTable.update(
            {
                # GeneralModuleStatus
                1: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # SpecificModuleStatus
                2: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # CurrentTime
                3: Value("type='TYPE_TIMESTAMP'\nsize=4\nlength=4\nunit='UNIX'\nscale=0"),
                # Voltage
                4: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # Temperature
                11: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # CurrentIP
                14: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # TotalCurrent
                17: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                # TotalRealPower
                18: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                # CurrentSubNetMask
                34: Value("type='TYPE_SUBNETMASK'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # CurrentDNSServer
                35: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # CurrentDNSServer
                36: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # HighCurrent(DC Current)
                41: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # UpsCommunicationStatus
                42: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # HighPower(DC Power)
                43: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # TotalHighCurrent
                44: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # TotalHighPower
                45: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # PositiveEnergy
                46: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                # NegativeEnergy
                47: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                # TotalPositiveEnergy
                48: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                # TotalNegativeEnergy
                49: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit='kWh'\nscale=3"),
                # Maxvoltage
                5004: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                # Minvoltage
                5005: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='V'\nscale=2"),
                # MinTemp.
                5006: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
                # MaxTemp
                5007: Value("type='TYPE_UNSIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='C'\nscale=1"),
                # MinHighCurrent
                5024: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MaxHighCurrent
                5025: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MinHighPower
                5026: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=2"),
                # MaxHighPower
                5027: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=2"),
                # MinTotalHCur
                5028: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MaxTotalHCur
                5029: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='A'\nscale=1"),
                # MinTotalHPow
                5030: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=2"),
                # MaxTotalHPow
                5031: Value("type='TYPE_SIGNED_NUMBER_WITH_TS'\nsize=6\nlength=6\nunit='kW'\nscale=2"),
                # Address
                10000: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # ModuleName
                10001: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # FirmwareVersion
                10002: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # HardwareVersion
                10003: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # FirmwareID
                10004: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # HardwareID
                10005: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # RackName
                10006: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # RackPosition
                10007: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # TemperatureUnitSelector
                10010: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # IPAddress
                10011: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # SubNetMask
                10012: Value("type='TYPE_SUBNETMASK'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # StdGateway
                10013: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # DnsServer
                10014: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # MAC
                10015: Value("type='TYPE_MAC'\nsize=6\nlength=6\nunit=''\nscale=0"),
                # DHCPEnable
                10016: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # NTPServer
                10017: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # UseDefaultNTPServer
                10018: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # UseNTP
                10019: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # SNMPTrapRecvIP
                10020: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # SNMPTrapRecvPort
                10021: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # SNMPCommunityRead
                10022: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                # SNMPCommunityWrite
                10023: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                # SNMPControl
                10024: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ECSServer
                10028: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # UseECSServer
                10029: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # DisplayLock
                10031: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # DisplayTimeOn
                10032: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='min'\nscale=0"),
                # DisplayRotation
                10033: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                10039: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=3"),
                # MaxVoltageWarning
                10047: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # MinVoltageWarning
                10049: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='V'\nscale=2"),
                # MinTemperatureWarning
                10052: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # MaxTemperatureWarning
                10053: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='C'\nscale=1"),
                # SNMPTrapCommunity
                10073: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                # GeneralEventEnable
                10074: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # SNMPSysContact
                10075: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # CurrentWarningEvent
                10078: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # PowerWarningEvent
                10080: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # TotalCurrentWarningEvent
                10082: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # TotalPowerWarningEvent
                10084: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # VoltageWarningEvent
                10086: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # TemperatureWarningEvent
                10087: Value("type='TYPE_EVENTFLAGS'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ECSServerPort
                10106: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # ExternalSensorLabel
                10109: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                # HttpsOnly
                10127: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # TelnetSsl
                10128: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # CookieTimeToLive
                10130: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit=''\nscale=0"),
                # DeviceID
                10150: Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"),
                # DeviceVersion
                10151: Value("type='TYPE_VERSION'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # SysName
                10152: Value("type='TYPE_STRING'\nsize=16\nlength=16\nunit=''\nscale=0"),
                # DebugIPAddress
                10162: Value("type='TYPE_IP'\nsize=4\nlength=4\nunit=''\nscale=0"),
                # MaxHighCurrentWarning
                10165: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # RecoveryPwrThresh
                10171: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='W'\nscale=0"),
                # MinHighCurrentWarning
                10176: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # MinHighPowerWarning
                10177: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # MaxHighPowerWarning
                10178: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # HeartbeatInterval
                10179: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit='kW'\nscale=0"),
                # MinTotalHCurrWarn
                10180: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # MaxTotalHCurrWarn
                10181: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=2\nlength=2\nunit='A'\nscale=1"),
                # MinTotalHPowerWarn
                10182: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # MaxTotalHPowerWarn
                10183: Value("type='TYPE_SIGNED_NUMBER'\nsize=2\nlength=2\nunit='kW'\nscale=2"),
                # JumpBoot
                40000: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40002: Value("type='TYPE_COMMAND'\nsize=16\nlength=16\nunit=''\nscale=0"),
                40003: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40004: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40005: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40006: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40007: Value("type='TYPE_UNSIGNED_NUMBER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModInfo
                40008: Value("type='TYPE_STRING'\nsize=26\nlength=26\nunit=''\nscale=0"),
                40009: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40010: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40011: Value("type='TYPE_ENUM'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40012: Value("type='TYPE_STRING'\nsize=32\nlength=32\nunit=''\nscale=0"),
                40013: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40014: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                40015: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModStatus
                40018: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleManagement
                40026: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # ModuleScan
                40027: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50000: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                # Parameter
                50001: Value("type='TYPE_POINTER'\nsize=1\nlength=1\nunit=''\nscale=0"),
                50011: Value("type='TYPE_RAW'\nsize=16\nlength=16\nunit=''\nscale=0"),
                60001: Value("type='TYPE_COMMAND'\nsize=1\nlength=1\nunit=''\nscale=0"),
            }
        )

    def getModuleName(self):
        guid = 10001
        portnumber = 0
        length = 1
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setModuleName(self, value):
        guid = 10001
        portnumber = 0
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getFirmwareVersion(self, moduleID="M1"):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getFirmwareVersionStr(self, moduleID="M1"):
        guid = 10002
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getHardwareVersion(self, moduleID="M1"):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareVersion' GUID  10003 Data type TYPE_VERSION_FULL
    # Hardware version
    # Return the hardware version as a string (example: '1.2.0.6')
    def getHardwareVersionStr(self, moduleID="M1"):
        guid = 10003
        portnumber = 0
        length = 1
        valDef = copy(self._guidTable[guid])
        valDef.type = "TYPE_VERSION_FULL"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'FirmwareID' GUID  10004 Data type TYPE_STRING
    # Identification of the firmware
    def getFirmwareID(self, moduleID="M1"):
        guid = 10004
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Attribute 'HardwareID' GUID  10005 Data type TYPE_STRING
    # Identification of the hardware
    def getHardwareID(self, moduleID="M1"):
        guid = 10005
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPowerPointer(self):
        """Return all available data for this master module."""
        moduleID = "M1"
        return self._getPointerData(moduleID)

    def getVoltage(self, feedNumber):
        """
        @param feedNumber: can be 1 or 2
        """
        moduleID = "M1"
        guid = 4
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, feedNumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getCurrent(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        moduleID = "M1"
        guid = 41
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getTotalCurrent(self, feedNumber):
        moduleID = "M1"
        guid = 44
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, feedNumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPower(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        moduleID = "M1"
        guid = 43
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getTotalPower(self, feedNumber):
        moduleID = "M1"
        guid = 45
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, feedNumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getPositiveActiveEnergy(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        moduleID = "M1"
        guid = 46
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getTotalPositiveActiveEnergy(self, feedNumber):
        moduleID = "M1"
        guid = 48
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, feedNumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getNegativeActiveEnergy(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        moduleID = "M1"
        guid = 47
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getTotalNegativeActiveEnergy(self, feedNumber):
        moduleID = "M1"
        guid = 49
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, feedNumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def getSNMPTrapRecvIP(self, portnumber):
        guid = 10020
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvIP(self, value, portnumber):
        guid = 10020
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getSNMPTrapRecvPort(self, portnumber):
        guid = 10021
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setSNMPTrapRecvPort(self, value, portnumber):
        guid = 10021
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # GeneralEventEnable
    def getGeneralEventEnable(self):
        guid = 10074
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setGeneralEventEnable(self, value):
        guid = 10074
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

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

    def getMaxCurrentWarning(self, portnumber):
        guid = 10165
        valDef = self._guidTable[guid]
        moduleID = "M1"
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxCurrentWarning(self, value, portnumber):
        guid = 10165
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMinCurrentWarning(self, portnumber):
        guid = 10176
        valDef = self._guidTable[guid]
        moduleID = "M1"
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinCurrentWarning(self, value, portnumber):
        guid = 10176
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMaxPowerWarning(self, portnumber):
        guid = 10178
        valDef = self._guidTable[guid]
        moduleID = "M1"
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxPowerWarning(self, value, portnumber):
        guid = 10178
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMinPowerWarning(self, portnumber):
        guid = 10177
        valDef = self._guidTable[guid]
        moduleID = "M1"
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinPowerWarning(self, value, portnumber):
        guid = 10177
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMaxTemperatureWarning(self):
        guid = 10053
        valDef = self._guidTable[guid]
        moduleID = "M1"
        portnumber = 0
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxTemperatureWarning(self, value):
        guid = 10053
        valDef = self._guidTable[guid]
        moduleID = "M1"
        portnumber = 0
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMinTemperatureWarning(self):
        guid = 10052
        valDef = self._guidTable[guid]
        moduleID = "M1"
        portnumber = 0
        length = 1
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinTemperatureWarning(self, value):
        guid = 10052
        valDef = self._guidTable[guid]
        moduleID = "M1"
        portnumber = 0
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMaxVoltageWarning(self, portnumber=1):
        guid = 10047
        length = 1
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMaxVoltageWarning(self, value, portnumber=1):
        guid = 10047
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    def getMinVoltageWarning(self, portnumber=1):
        guid = 10049
        length = 1
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setMinVoltageWarning(self, value, portnumber=1):
        guid = 10049
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # CurrentWarningEvent
    def getCurrentWarningEvent(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        guid = 10078
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setCurrentWarningEvent(self, portnumber, value):
        """
        @param portnumber: can be from 1 to 12
        """
        guid = 10078
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # PowerWarningEvent
    def getPowerWarningEvent(self, portnumber):
        """
        @param portnumber: can be from 1 to 12
        """
        guid = 10080
        moduleID = "M1"
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setPowerWarningEvent(self, portnumber, value):
        """
        @param portnumber: can be from 1 to 12
        """
        guid = 10080
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # TemperatureWarningEvent
    def getTemperatureWarningEvent(self):
        guid = 10087
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setTemperatureWarningEvent(self, value):
        guid = 10087
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # VoltageWarningEvent
    def getVoltageWarningEvent(self, portnumber=1):
        guid = 10086
        length = 1
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    def setVoltageWarningEvent(self, portnumber, value):
        guid = 10086
        valDef = self._guidTable[guid]
        moduleID = "M1"
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Attribute 'ModInfo' GUID  40008 Data type TYPE_COMMAND
    def getModInfo(self, portnumber=1, length=1):
        guid = 40008
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Returns modules statuses; the data returned can be used to see if the
    # modules are active, present, monitored or managed
    def getModStatus(self):
        guid = 40018
        moduleID = "M1"
        portnumber = 1
        length = 32
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Sets management value for modules
    # 0 - released, 1- managed
    def setModuleManagement(self, value, portnumber=2):
        guid = 40026
        moduleID = "M1"
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)

    # Get  to request status of module scan.
    # (idle = 0, busy = 1, success = 2, fail = 3)
    def getModuleScan(self):
        guid = 40027
        moduleID = "M1"
        portnumber = 0
        length = 1
        valDef = self._guidTable[guid]
        data = self._parent.client.getAttribute(moduleID, guid, portnumber, length)
        return self._parent.getObjectFromData(data, valDef, count=length)

    # Set to 1 to start a new module scan.
    def setModuleScan(self, value=1):
        guid = 40027
        moduleID = "M1"
        portnumber = 0
        valDef = self._guidTable[guid]
        data = self._parent.client.setAttribute(moduleID, guid, convert.value2bin(value, valDef), portnumber)
        return self._parent.getObjectFromData(data, valDef, setter=True)
