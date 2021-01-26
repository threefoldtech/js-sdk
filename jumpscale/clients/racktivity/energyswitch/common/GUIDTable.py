# pylint: disable=W0201


class Value:
    def __init__(self, initStr=None, **kwargs):
        # Initialize everything with None
        self.fields = ("type", "size", "length", "unit", "version", "scale", "min", "max")
        for field in self.fields:
            setattr(self, field, None)

        if initStr:
            self.load(initStr)
        else:
            for name, value in kwargs.items():
                setattr(self, name, value)

    def save(self):
        r = ""
        for field in self.fields:
            val = getattr(self, field)
            if val is None:
                continue

            r += field + "=" + repr(val) + "\n"
        return r.strip()

    def load(self, _str):
        for line in _str.split("\n"):
            (key, val) = line.split("=", 1)
            setattr(self, key, eval(val))


class Functions:
    # Variables

    def __init__(self):
        self.guid = None
        self.name = None
        self.description = ""
        self.valDef = None
        self.read = False
        self.write = False
        self.default = ""


functions = {}

func = Functions()
functions[1] = func
func.guid = 1
func.name = "GeneralModuleStatus"
func.description = "General status of a module"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[2] = func
func.guid = 2
func.name = "SpecificModuleStatus"
func.description = ""
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[3] = func
func.guid = 3
func.name = "CurrentTime"
func.description = "Unix timestamp of the current time"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_TIMESTAMP"
func.valDef.size = 4
func.valDef.unit = "UNIX"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[4] = func
func.guid = 4
func.name = "Voltage"
func.description = "True RMS Voltage"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5] = func
func.guid = 5
func.name = "Frequency"
func.description = "Frequency"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "Hz"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[6] = func
func.guid = 6
func.name = "Current"
func.description = "Current true RMS"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[7] = func
func.guid = 7
func.name = "Power"
func.description = "Real Power"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[8] = func
func.guid = 8
func.name = "StatePortCur"
func.description = "current port state"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[9] = func
func.guid = 9
func.name = "ActiveEnergy"
func.description = "Active Energy"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "kWh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10] = func
func.guid = 10
func.name = "ApparentEnergy"
func.description = "Apparent Energy"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "kVAh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[11] = func
func.guid = 11
func.name = "Temperature"
func.description = "Temperature"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "C"
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[12] = func
func.guid = 12
func.name = "Humidity"
func.description = "Humidity"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "%RH"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[13] = func
func.guid = 13
func.name = "FanSpeed"
func.description = "Fanspeed in Rounds per minute"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "rpm"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5000] = func
func.guid = 5000
func.name = "MaxCurrent"
func.description = "Maximum port current occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5001] = func
func.guid = 5001
func.name = "MaxPower"
func.description = "Maximum port power occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5002] = func
func.guid = 5002
func.name = "MaxTotalCurrent"
func.description = "Maximum total current occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5003] = func
func.guid = 5003
func.name = "MaxTotalPower"
func.description = "Maximum total power occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 8
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[5004] = func
func.guid = 5004
func.name = "MaxVoltage"
func.description = "Maximum voltage occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5005] = func
func.guid = 5005
func.name = "MinVoltage"
func.description = "Minimum voltage occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5006] = func
func.guid = 5006
func.name = "MinTemperature"
func.description = "Minimum temperature occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "C"
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[5007] = func
func.guid = 5007
func.name = "MaxTemperature"
func.description = "Maximum temperature occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "C"
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[5008] = func
func.guid = 5008
func.name = "MinHumidity"
func.description = "Minimum humidity occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "%RH"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5009] = func
func.guid = 5009
func.name = "MaxHumidity"
func.description = "Maximum humidity occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "%RH"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10000] = func
func.guid = 10000
func.name = "Address"
func.description = "Identification of the module"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10001] = func
func.guid = 10001
func.name = "ModuleName"
func.description = "Module name"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10002] = func
func.guid = 10002
func.name = "FirmwareVersion"
func.description = "Firmware version"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_VERSION"
func.valDef.size = 4


func = Functions()
functions[10003] = func
func.guid = 10003
func.name = "HardwareVersion"
func.description = "Hardware version"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_VERSION"
func.valDef.size = 4


func = Functions()
functions[10004] = func
func.guid = 10004
func.name = "FirmwareID"
func.description = "Identification of the firmware"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 8


func = Functions()
functions[10005] = func
func.guid = 10005
func.name = "HardwareID"
func.description = "Identification of the hardware"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 8


func = Functions()
functions[10006] = func
func.guid = 10006
func.name = "RackName"
func.description = "Rack Name"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10007] = func
func.guid = 10007
func.name = "RackPosition"
func.description = "Position of the Energy Switch in the rack"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10008] = func
func.guid = 10008
func.name = "AdminLogin"
func.description = "Admin Login"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10009] = func
func.guid = 10009
func.name = "AdminPassword"
func.description = "Admin Password"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10010] = func
func.guid = 10010
func.name = "TemperatureUnitSelector"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10011] = func
func.guid = 10011
func.name = "IPAddress"
func.description = "IP-address"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10012] = func
func.guid = 10012
func.name = "SubNetMask"
func.description = "Subnetmask"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SUBNETMASK"
func.valDef.size = 4


func = Functions()
functions[10013] = func
func.guid = 10013
func.name = "StdGateWay"
func.description = "Standard gateway IP"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10014] = func
func.guid = 10014
func.name = "DnsServer"
func.description = "Dns server IP"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10015] = func
func.guid = 10015
func.name = "MAC"
func.description = "MAC address"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_MAC"
func.valDef.size = 6


func = Functions()
functions[10016] = func
func.guid = 10016
func.name = "DHCPEnable"
func.description = "DHCP enable"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10017] = func
func.guid = 10017
func.name = "NTPServer"
func.description = "NTP server IP"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10018] = func
func.guid = 10018
func.name = "UseDefaultNTPServer"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10019] = func
func.guid = 10019
func.name = "UseNTP"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10020] = func
func.guid = 10020
func.name = "SNMPTrapRecvIP"
func.description = "SNMP trap server IP-address"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10021] = func
func.guid = 10021
func.name = "SNMPTrapRecvPort"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10022] = func
func.guid = 10022
func.name = "SNMPCommunityRead"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10023] = func
func.guid = 10023
func.name = "SNMPCommunityWrite"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10024] = func
func.guid = 10024
func.name = "SNMPControl"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10025] = func
func.guid = 10025
func.name = "TelnetCLIPort"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10026] = func
func.guid = 10026
func.name = "TelnetUARTMUXPort"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10027] = func
func.guid = 10027
func.name = "SelectUARTMUCChannel"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10028] = func
func.guid = 10028
func.name = "LDAPServer"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10029] = func
func.guid = 10029
func.name = "UseLDAPServer"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10030] = func
func.guid = 10030
func.name = "Beeper"
func.description = "Beeper control enable beeper for n seconds"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "s"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10031] = func
func.guid = 10031
func.name = "DisplayLock"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10032] = func
func.guid = 10032
func.name = "DisplayTimeOn"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "min"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10033] = func
func.guid = 10033
func.name = "DisplayRotation"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10034] = func
func.guid = 10034
func.name = "PortName"
func.description = "Name of the port"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10035] = func
func.guid = 10035
func.name = "PortState"
func.description = (
    "The state of the port, only used to set the port state, see current port state to get the port state"
)
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10036] = func
func.guid = 10036
func.name = "CurrentPriorOff"
func.description = "Priority level switch off when maximum total current exceeds threshold"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "1H8L"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10037] = func
func.guid = 10037
func.name = "DelayOn"
func.description = "Port activation delay after power recycle"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "s"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10038] = func
func.guid = 10038
func.name = "MaxCurrentOff"
func.description = "Maximum port current switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10039] = func
func.guid = 10039
func.name = "MaxCurrentWarning"
func.description = "Maximum port current warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10040] = func
func.guid = 10040
func.name = "MaxPowerOff"
func.description = "Maximum port power switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10041] = func
func.guid = 10041
func.name = "MaxPowerWarning"
func.description = "Maximum port power warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10042] = func
func.guid = 10042
func.name = "MaxTotalCurrentOff"
func.description = "Maximum total current switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10043] = func
func.guid = 10043
func.name = "MaxTotalCurrentWarning"
func.description = "Maximum total current warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10044] = func
func.guid = 10044
func.name = "MaxTotalPowerOff"
func.description = "Maximum total power switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10045] = func
func.guid = 10045
func.name = "MaxTotalPowerWarning"
func.description = "Maximum total power warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10046] = func
func.guid = 10046
func.name = "MaxVoltageOff"
func.description = "Maximum voltage switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10047] = func
func.guid = 10047
func.name = "MaxVoltageWarning"
func.description = "Maximum voltage warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10048] = func
func.guid = 10048
func.name = "MinVoltageOff"
func.description = "Minimum voltage switch off level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10049] = func
func.guid = 10049
func.name = "MinVoltageWarning"
func.description = "Minimum voltage warning level"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "V"
func.valDef.scale = 2
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10050] = func
func.guid = 10050
func.name = "ActiveEnergyReset"
func.description = "Active Energy"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 8
func.valDef.unit = "kWh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10051] = func
func.guid = 10051
func.name = "ApparentEnergyReset"
func.description = "Apparent Energy"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 8
func.valDef.unit = "kVAh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10052] = func
func.guid = 10052
func.name = "MinTemperatureWarning"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "C"
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[10053] = func
func.guid = 10053
func.name = "MaxTemperatureWarning"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "C"
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[10054] = func
func.guid = 10054
func.name = "MinHumidityWarning"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "%RH"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10055] = func
func.guid = 10055
func.name = "MaxHumidityWarning"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "%RH"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[10056] = func
func.guid = 10056
func.name = "LedStatus"
func.description = "To set Status of a led"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10057] = func
func.guid = 10057
func.name = "MatrixDisplayStatus"
func.description = "To set Status of a small matrix display"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10058] = func
func.guid = 10058
func.name = "Baudrate"
func.description = "To set baudrate for circular buffers"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[10059] = func
func.guid = 10059
func.name = "P_PID"
func.description = "Proportional value of PID"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10060] = func
func.guid = 10060
func.name = "I_PID"
func.description = "Integral value of PID"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10061] = func
func.guid = 10061
func.name = "D_PID"
func.description = "Derivative value of PID"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10062] = func
func.guid = 10062
func.name = "WeightOfTempsensor"
func.description = "Gives the weight of a tempsensor to the input of a PID controller"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10063] = func
func.guid = 10063
func.name = "TargetTemp"
func.description = "Temperature to be set for PID controller"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_SIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 1
func.valDef.min = -32768
func.valDef.max = 32768


func = Functions()
functions[10064] = func
func.guid = 10064
func.name = "MaximumPWM"
func.description = "Maximum value of pwm to control ventilators"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10065] = func
func.guid = 10065
func.name = "MinimumPWM"
func.description = "Minimum value of pwm to control ventilators"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10066] = func
func.guid = 10066
func.name = "Startuptime"
func.description = ""
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "s"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[40000] = func
func.guid = 40000
func.name = "JumpBoot"
func.description = "Enter bootloader mode. Normally this command is only sent to application program. When the bootloader is already running, this command will only reply a positive acknowledge."
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 0


func = Functions()
functions[40001] = func
func.guid = 40001
func.name = "GotoAddressmode"
func.description = "Addressing mode on/off"
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[40002] = func
func.guid = 40002
func.name = "GotoFactoryMode"
func.description = ""
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 16


func = Functions()
functions[40003] = func
func.guid = 40003
func.name = "DoSnapshot"
func.description = ""
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[40004] = func
func.guid = 40004
func.name = "SampleChannelTime"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[40005] = func
func.guid = 40005
func.name = "SampleChannelFFT"
func.description = ""
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[40006] = func
func.guid = 40006
func.name = "FlushCallibData"
func.description = ""
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[40007] = func
func.guid = 40007
func.name = "ModNum"
func.description = (
    "To retrieve the number of modules connected to the device. The device itself is treated as module 0."
)
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[40008] = func
func.guid = 40008
func.name = "ModInfo"
func.description = "To retrieve module information"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 26


func = Functions()
functions[40009] = func
func.guid = 40009
func.name = "ApplyIPSettings"
func.description = ""
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[50000] = func
func.guid = 50000
func.name = "Monitor"
func.description = "Get the monitor values"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_POINTER"


func = Functions()
functions[50001] = func
func.guid = 50001
func.name = "Parameter"
func.description = "get all parameters"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_POINTER"


func = Functions()
functions[50002] = func
func.guid = 50002
func.name = "CircularReadBuffer"
func.description = "Read from slave(application connected to rs232) to master or from master to application"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_CIRCULAR_BUFFER"
func.valDef.size = 1


func = Functions()
functions[50003] = func
func.guid = 50003
func.name = "CircularWriteBuffer"
func.description = "Write of data from application to master or from master to slave(application connected to rs232)"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_CIRCULAR_BUFFER"
func.valDef.size = 1


func = Functions()
functions[50004] = func
func.guid = 50004
func.name = "VoltageTimeSamples"
func.description = "Get the voltage samples in oscilloscope view mode"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 1


func = Functions()
functions[50005] = func
func.guid = 50005
func.name = "CurrentTimeSamples"
func.description = "Get the current samples in oscilloscope view mode"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 1


func = Functions()
functions[50006] = func
func.guid = 50006
func.name = "VoltageFreqSamples"
func.description = "Get the frequency analyse of the voltage"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 1


func = Functions()
functions[50007] = func
func.guid = 50007
func.name = "CurrentFreqSamples"
func.description = "Get the frequency analyse of the current"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 1


func = Functions()
functions[50008] = func
func.guid = 50008
func.name = "Eeprom"
func.description = "read or write eeprom data"
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 1


func = Functions()
functions[50009] = func
func.guid = 50009
func.name = "CallibrationValues"
func.description = ""
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_RAW"
func.valDef.size = 2


func = Functions()
functions[60000] = func
func.guid = 60000
func.name = "BootReadID"
func.description = "Get the identification of the microcontroller. The response contains the values stored at memory address 0xFF0000 and 0xFF00002. (8 bytes in total)"
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[60001] = func
func.guid = 60001
func.name = "BootJumpApp"
func.description = "Jump to the application, which starts at 0x4000.  "
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 0


func = Functions()
functions[40013] = func
func.guid = 40013
func.name = "UDPUser"
func.description = "User mode for UDP commands"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[60002] = func
func.guid = 60002
func.name = "BootXTEA"
func.description = "Process a block of encrypted program memory data. The decrypted data will then be written into the program (flash) memory."
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[60004] = func
func.guid = 60004
func.name = "BootErase"
func.description = "Erase a page of program memory. The message takes one parameter, i.e. the page number. Valid page number for the dsPICFJ256 are from 16 to 170."
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[60005] = func
func.guid = 60005
func.name = "BootPageRange"
func.description = (
    "To get the number of pages of the application firmware memory. Only pages within this range can be erased."
)
func.read = 0
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[60010] = func
func.guid = 60010
func.name = "BootParameters"
func.description = "To set or retrieve the parameters of the device stored in flash during production (factory mode) such as:  -    Application firmware id (RTF-number) -  Application firmware version -  Hardware ID (RTH-number) -  Hardware version -  UID "
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = ""
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[40010] = func
func.guid = 40010
func.name = "DHCPReset"
func.description = "Reset DHCP"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1


func = Functions()
functions[14] = func
func.guid = 14
func.name = "CurrentIP"
func.description = "Gives the current IP. When DHCP is on, you can see here what ip is given by the DHCP server"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_IP"
func.valDef.size = 4


func = Functions()
functions[10067] = func
func.guid = 10067
func.name = "UserLogin"
func.description = "User Login"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10068] = func
func.guid = 10068
func.name = "UserPassword"
func.description = "User Password"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10069] = func
func.guid = 10069
func.name = "RestrictedUserLogin"
func.description = "Restricted User Login"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[10070] = func
func.guid = 10070
func.name = "RestrictedUserPassword"
func.description = "Restricted User Password"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 16


func = Functions()
functions[60020] = func
func.guid = 60020
func.name = "BootAppFwID"
func.description = "Identification of the firmware"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 8


func = Functions()
functions[60021] = func
func.guid = 60021
func.name = "BootAppFwVersion"
func.description = "Identification of the hardware"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_VERSION"
func.valDef.size = 4


func = Functions()
functions[15] = func
func.guid = 15
func.name = "ApparentPower"
func.description = "Apparent power (this is the product of the current and the voltage)"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "VA"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[16] = func
func.guid = 16
func.name = "PowerFactor"
func.description = "Powerfactor "
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[5010] = func
func.guid = 5010
func.name = "MinCurrent"
func.description = "Minimum port current occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5011] = func
func.guid = 5011
func.name = "MinPower"
func.description = "Minimum port power occured since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5012] = func
func.guid = 5012
func.name = "MinPowerFactor"
func.description = "Minimum powerfactor occured per port since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 5
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[5013] = func
func.guid = 5013
func.name = "MaxPowerFactor"
func.description = "Maximum powerfactor occured per port since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 5
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[17] = func
func.guid = 17
func.name = "TotalCurrent"
func.description = "Total current"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 2
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[18] = func
func.guid = 18
func.name = "TotalRealPower"
func.description = "Total real power"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[19] = func
func.guid = 19
func.name = "TotalApparentPower"
func.description = "Total apparent power"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "VA"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[20] = func
func.guid = 20
func.name = "TotalActiveEnergy"
func.description = "Total active energy"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "kWh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[21] = func
func.guid = 21
func.name = "TotalApparentEnergy"
func.description = "Total apparent energy"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 4
func.valDef.unit = "kVAh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[22] = func
func.guid = 22
func.name = "TotalPowerFactor"
func.description = "Total power factor"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER"
func.valDef.size = 1
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[5014] = func
func.guid = 5014
func.name = "MinTotalCurrent"
func.description = "Minimum port current occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "A"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5015] = func
func.guid = 5015
func.name = "MinTotalPower"
func.description = "Minimum port power occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 6
func.valDef.unit = "W"
func.valDef.scale = 1
func.valDef.min = 0
func.valDef.max = 65536


func = Functions()
functions[5016] = func
func.guid = 5016
func.name = "MinTotalPowerFactor"
func.description = "Minimum total power factor occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 5
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[5017] = func
func.guid = 5017
func.name = "MaxTotalPowerFactor"
func.description = "Maximum total power factor occurred since last reset"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_UNSIGNED_NUMBER_WITH_TS"
func.valDef.size = 5
func.valDef.unit = "%"
func.valDef.scale = 0
func.valDef.min = 0
func.valDef.max = 256


func = Functions()
functions[10071] = func
func.guid = 10071
func.name = "ActiveTotalEnergyReset"
func.description = "Active Total Energy / time of reset + value at that time"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 8
func.valDef.unit = "kWh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[10072] = func
func.guid = 10072
func.name = "ApparentTotalEnergyReset"
func.description = "Apparent Total Energy / time of reset + value at that time"
func.read = 1
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 8
func.valDef.unit = "kVAh"
func.valDef.scale = 3
func.valDef.min = 0
func.valDef.max = 4294967296


func = Functions()
functions[50010] = func
func.guid = 50010
func.name = "MonitorAutoRefresh"
func.description = "Get the monitor values from the module that are auto refreshed"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_POINTER"


func = Functions()
functions[40011] = func
func.guid = 40011
func.name = "Role"
func.description = "To see in which role you are logged in"
func.read = 1
func.write = 0
func.valDef = Value()
func.valDef.type = "TYPE_ENUM"
func.valDef.size = 1


func = Functions()
functions[40012] = func
func.guid = 40012
func.name = "UserLoginAndPassword"
func.description = "Contains 1 loginname and 1 password"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_STRING"
func.valDef.length = 32


func = Functions()
functions[40014] = func
func.guid = 40014
func.name = "DoHotReset"
func.description = "Hot reset of the device"
func.read = 0
func.write = 1
func.valDef = Value()
func.valDef.type = "TYPE_COMMAND"
func.valDef.size = 1
