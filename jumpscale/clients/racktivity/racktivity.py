import time

from jumpscale.clients.racktivity.energyswitch.proxy import connection
from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.clients.racktivity.energyswitch.modelfactory.modelfactory import ModelFactory
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j


class RackSal(Client):
    MODULE_INFO = (40031, 0, 1, Value("type='TYPE_VERSION_FULL'\nsize=4\nLength=4\nunit=''\nscale=0"))
    username = fields.String(required=True)
    password = fields.String(required=True)
    hostname = fields.String(required=True)
    port = fields.Integer(required=True)

    def __init__(self, rtf=None, moduleinfo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None
        self.__master_inited = False
        self.__master = None
        self.__rtf = rtf
        self.__power_inited = False
        self.__power = None
        self.__sensor_inited = False
        self.__sensor = None
        self.__display_inited = False
        self.__display = None
        self.__slave_power_inited = False
        self.__slave_power = None
        self.__factory = None
        self.__moduleinfo = moduleinfo or {}

    @property
    def client(self):
        if not self.__client:
            self.__client = connection.Connect(self.username, self.password, self.hostname, self.port)
        return self.__client

    @property
    def factory(self):
        if not self.factory:
            self.client
            self.__factory = ModelFactory(self.client, self.__rtf)
        return self.__factory

    @property
    def master(self):
        if self.__master_inited is False:
            self.__master_inited = True
            self.__master = self.__factory.get_master(self.__moduleinfo.get("M"))(self)
        return self.__master

    @property
    def power(self):
        if self.__power_inited is False:
            self.__power_inited = True
            power_class = self.__factory.get_power(self.__moduleinfo.get("P"))
            if power_class:
                self.__power = power_class(self)
            else:
                self.__power = None
        return self.__power

    @property
    def sensor(self):
        if self.__sensor_inited is False:
            self.__sensor_inited = True
            # sal does not handle now sensors with different versions
            sensor_class = self.__factory.get_sensor(self.__moduleinfo.get("A"))
            if sensor_class:
                self.__sensor = sensor_class(self)
            else:
                self.__sensor = None
        return self.__sensor

    @property
    def display(self):
        if self.__display_inited is False:
            self.__display_inited = True
            # sal does not handle now displays with different versions
            display_class = self.__factory.get_display(self.__moduleinfo.get("D"))
            if display_class:
                self.__display = display_class(self)
            else:
                self.__display = None
        return self.__display

    @property
    def slave_power(self):
        if self.__slave_power_inited is False:
            self.__slave_power_inited = True
            # sal does not handle now slave_powers with different versions
            slave_power_class = self.__factory.get_slave_power(self.__moduleinfo.get("Q"))
            if slave_power_class:
                self.__slave_power = slave_power_class(self)
            else:
                self.__slave_power = None
        return self.__slave_power

    def getObjectFromData(self, data, valDef, setter=False, count=1):
        if setter:
            return convert.bin2int(data)
        if count == 1:
            return convert.bin2value(data, valDef)
        if data[0] != "\0":  # pylint: disable=W1401
            # This is an error code, return it
            return convert.bin2value(data, valDef)
        # Remove the error byte
        data = data[1:]
        # get length of each port
        length = len(data) / count
        # Split the ports
        data_list = convert.slice_string(data, length)
        result = []
        for data in data_list:
            result.append(convert.bin2value(data, valDef, checkErrorByte=False)[1])
        return 0, result

    def getModuleVersion(self, moduleID):
        """
        this function returns the module version or None
        """
        guid, portnumber, length, valdef = self.MODULE_INFO
        data = self.client.getAttribute(moduleID, guid, portnumber, length)
        code, version = convert.bin2value(data, valdef)
        if not code:
            return version

    def logout(self):
        self.client.logout()

    def translateDetailedLog(self, moduleID, binaryfile, csvfile, headerNames=None):
        """
        decodes detailed logging
        @param moduleID - module to get log for (Mx, Px, Ax)
        @param binaryfile - filename of binary log
        @param csvfile - filename for csv
        """

        def prepareValue(value, info):
            result = []
            if isinstance(value, list):
                for val in value:
                    result.extend(prepareValue(val, info))
            elif isinstance(value, str):
                result.append('"%s"' % value)
            elif isinstance(value, tuple):
                result.append(str(round(value[0], 3)))
                result.append('"%s"' % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(value[1])))
            else:
                if info[1].type == "TYPE_TIMESTAMP":
                    result.append('"%s"' % time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(value)))
                else:
                    result.append(str(round(value, 3)))

            return result

        def prepareHeader(info, nr=None):
            hdr = []
            if info[2] > 1 and nr is None:
                for i in range(info[2]):
                    hdr.append(prepareHeader(info, i + 1))
            else:
                tmpl = "%s"
                if nr:
                    tmpl += " (%d)" % nr
                if isinstance(headerNames, dict) and info[0] in headerNames:
                    name = headerNames[info[0]]
                else:
                    name = str(info[0])
                hdr.append(tmpl % name)
                if info[1].type.endswith("_WITH_TS"):
                    hdr.append(tmpl % ("%s timestamp" % name))
            return ", ".join(hdr)

        def calculatePointerSize(structure):
            size = 0
            for elem in structure:
                size += elem[2] * elem[1].size

            return size

        if moduleID[0] == "M":
            paramInfo = self.master.definePointerStructure()
        elif moduleID[0] == "P" and self.power:
            paramInfo = self.power.definePointerStructure()
        elif moduleID[0] == "A" and self.sensor:
            paramInfo = self.sensor.definePointerStructure()
        elif moduleID[0] == "Q" and self.slave_power:
            paramInfo = self.slave_power.definePointerStructure()
        else:
            raise j.exceptions.Value("Requested moduleID not found")

        chunk = calculatePointerSize(paramInfo)

        # prepare header information
        lineData = []
        for idx, info in enumerate(paramInfo):
            if info[0] < 3:
                continue
            lineData.append(prepareHeader(info))

        with open(csvfile, "w") as out:
            out.write(", ".join(lineData))
            out.write("\n")
            with open(binaryfile, "rb") as fp:
                while True:
                    data = fp.read(chunk)
                    if not data:
                        break
                    try:
                        array = convert.pointer2values(data, paramInfo)
                    except IndexError:
                        break
                    lineData = []
                    for idx, info in enumerate(paramInfo):
                        if info[0] < 3:
                            continue
                        lineData.extend(prepareValue(array[idx], info))

                    out.write(", ".join(lineData))
                    out.write("\n")
