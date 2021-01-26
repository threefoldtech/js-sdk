import fnmatch
import logging
import os
import re
import sys
import zipfile

from jumpscale.clients.racktivity.energyswitch.common import convert
from jumpscale.clients.racktivity.energyswitch.common.GUIDTable import Value
from jumpscale.loader import j


class ModelFactory:
    FIRMWARE_ID = (10004, 0, 1, Value("type='TYPE_STRING'\nsize=8\nlength=8\nunit=''\nscale=0"))
    MODULE_INFO = (40031, 0, 1, Value("type='TYPE_VERSION_FULL'\nsize=4\nLength=4\nunit=''\nscale=0"))
    FIRMWARE_INFO = (10002, 0, 1, Value("type='TYPE_VERSION_FULL'\nsize=4\nlength=4\nunit=''\nscale=0"))

    def __init__(self, client, rtf=None):
        self._client = client
        if not rtf:
            self._model_dir = self._get_firmware_id()
        else:
            self._model_dir = rtf

        self._master_models = {}
        self._power_models = {}
        self._sensor_models = {}
        self._display_models = {}
        self._slave_power_models = {}

        ip = self._client.get_url
        self._ip = ip[ip.rindex("/", 0, 10) + 1 : ip.rindex("/")]

        self._get_available_models()

    def _get_module_model(self, module_id, class_name, module_version=None):
        if self._client.basicAuth:
            # we need to use the pre 1.0 API
            from jumpscale.clients.racktivity.energyswitch.modelfactory import Model_pre_1_0  # pylint: disable=W0404

            if hasattr(Model_pre_1_0, class_name):
                return getattr(Model_pre_1_0, class_name)
            return None

        if not module_version:
            code, module_version = self._get_module_version(module_id)
            if code:
                # This means the module is not present
                if code == 16:
                    return None

                # check if this is firmware version 1.0 as this didn't support
                # module versions
                code, version = self._get_firmware_version()
                if code:
                    raise j.exceptions.RuntimeError("Can't get the firmware version of the device (%s)" % self._ip)

                version = str(version)
                if version.startswith("1.0"):
                    from jumpscale.clients.racktivity.energyswitch.modelfactory import (
                        Model_firmware_1_0,
                    )  # pylint: disable=W0404

                    return getattr(Model_firmware_1_0, class_name)
                else:
                    raise j.exceptions.RuntimeError("Can't get the module version of %s (%s)" % (module_id, self._ip))

        # get the closest model
        parts = str(module_version).split(".")
        tuple_version = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
        int_version = self._convert_version_to_int(tuple_version)
        version = self._get_closest_version(int_version, class_name, str(module_version))

        try:
            model_class = "models.%s.%s_%s" % (self._model_dir, class_name, version.replace(".", "_"))
            model = __import__(model_class, globals(), locals(), fromlist=["Model"], level=1)
            return model.Model
        except RuntimeError:
            raise j.exceptions.RuntimeError(
                "Unsupported module version '%s' for %s (%s)" % (version, module_id, self._ip)
            )

    def _get_module_version(self, module_id):
        guid, portnumber, length, valdef = self.MODULE_INFO
        data = self._client.getAttribute(module_id, guid, portnumber, length)
        return convert.bin2value(data, valdef)

    def _get_firmware_version(self):
        guid, portnumber, length, valdef = self.FIRMWARE_INFO
        data = self._client.getAttribute("M1", guid, portnumber, length)
        return convert.bin2value(data, valdef)

    def _get_firmware_id(self):
        guid, portnumber, length, valdef = self.FIRMWARE_ID
        data = self._client.getAttribute("M1", guid, portnumber, length)
        code, firmware_id = convert.bin2value(data, valdef)
        if code == 0:
            return firmware_id
        else:
            return ""

    def _list_dir_filtered(self, path, name_filter):
        files_to_return = []

        dir_content = os.listdir(path)
        for dir_entry in dir_content:
            fullpath = os.path.join(path, dir_entry)
            if fnmatch.fnmatch(dir_entry, name_filter):
                files_to_return.append(fullpath)

        return files_to_return

    def _get_available_models(self):
        def get_version(path):
            # Get the basename and remove the ".py" or ".pyc" extension
            filename = os.path.basename(path).rsplit(".", 1)[0]
            parts = filename.split("_")
            if len(parts) == 5:
                tuple_version = (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))
                int_version = self._convert_version_to_int(tuple_version)
                version = "%d.%d.%d.%d" % tuple_version
                return (int_version, version)
            return None, None

        def get_models_from_disk(self, model_dir_path):
            models = self._list_dir_filtered(model_dir_path, name_filter="Master_*.py*")
            for model in models:
                int_version, version = get_version(model)
                if version:
                    self._master_models[int_version] = version
            # get power models
            models = self._list_dir_filtered(model_dir_path, name_filter="Power_*.py*")
            for model in models:
                int_version, version = get_version(model)
                if version:
                    self._power_models[int_version] = version

            # get sensor models
            models = self._list_dir_filtered(model_dir_path, name_filter="Sensor_*.py*")
            for model in models:
                int_version, version = get_version(model)
                if version:
                    self._sensor_models[int_version] = version

            # get display models
            models = self._list_dir_filtered(model_dir_path, name_filter="Display_*.py*")
            for model in models:
                int_version, version = get_version(model)
                if version:
                    self._display_models[int_version] = version

            # get slave_power models
            models = self._list_dir_filtered(model_dir_path, name_filter="SlavePower_*.py*")
            for model in models:
                int_version, version = get_version(model)
                if version:
                    self._slave_power_models[int_version] = version

        def get_models_from_egg(self, egg_path, model_dir_path):
            rel_path = os.path.relpath(path=model_dir_path, start=egg_path) + os.path.sep
            search_str = r"^%s(.*\.pyc?$)" % rel_path
            master_str = r"^%s(Master_.*\.pyc?$)" % rel_path
            power_str = r"^%s(Power_.*\.pyc?$)" % rel_path
            sensor_str = r"^%s(Sensor_.*\.pyc?$)" % rel_path
            display_str = r"^%s(Display_.*\.pyc?$)" % rel_path
            slave_power_str = r"^%s(SlavePower_.*\.pyc?$)" % rel_path
            egg_file = zipfile.ZipFile(egg_path)
            file_names = egg_file.namelist()
            for filename in file_names:
                match = re.search(search_str, filename)
                if match and os.path.sep not in match.group(1):
                    if re.search(master_str, filename):
                        int_version, version = get_version(filename)
                        if version:
                            self._master_models[int_version] = version
                    elif re.search(power_str, filename):
                        int_version, version = get_version(filename)
                        if version:
                            self._power_models[int_version] = version
                    elif re.search(sensor_str, filename):
                        int_version, version = get_version(filename)
                        if version:
                            self._sensor_models[int_version] = version
                    elif re.search(display_str, filename):
                        int_version, version = get_version(filename)
                        if version:
                            self._display_models[int_version] = version
                    elif re.search(slave_power_str, filename):
                        int_version, version = get_version(filename)
                        if version:
                            self._slave_power_models[int_version] = version

        # get master models, power models, and sensor models
        j.logger.debug("{} {} {}".format(os.path.dirname(__file__), "models", self._model_dir))
        model_dir_path = os.path.join(os.path.dirname(__file__), "models", self._model_dir)
        match = re.search(r".*\.egg", model_dir_path)
        if not match:  # outside an egg, so listing files will work
            get_models_from_disk(self, model_dir_path)

        else:  # inside a python egg
            egg_path = match.group()
            get_models_from_egg(self, egg_path, model_dir_path)

    def _get_closest_version(self, version, class_name, version_str):
        models = self._master_models
        if class_name == "Power":
            models = self._power_models
        elif class_name == "Sensor":
            models = self._sensor_models
        elif class_name == "Display":
            models = self._display_models
        elif class_name == "SlavePower":
            models = self._slave_power_models

        closest = version
        closest_diff = -sys.maxsize
        for model_version in models:
            diff = model_version - version
            if diff > closest_diff and diff <= 0:  # only match versions downwards
                closest = model_version
                closest_diff = diff

        if closest not in models:
            msg = "Unable to find valid model for %s %s (%s)" % (class_name, version_str, self._ip)
            raise Exception(msg)

        return models[closest]

    def _convert_version_to_int(self, version):
        return version[3] + (version[2] * 256) + (version[1] * (256 * 256)) + (version[0] * (256 * 256 * 256))

    def get_master(self, module_version=None):
        return self._get_module_model("M1", "Master", module_version)

    def get_power(self, module_version=None):
        return self._get_module_model("P1", "Power", module_version)

    def get_sensor(self, module_version=None):
        if module_version:
            return self._get_module_model("Ax", "Sensor", module_version)

        for i in range(1, 8):
            module_id = "A%d" % i
            try:
                mm = self._get_module_model(module_id, "Sensor")
                if mm:
                    return mm
            except (RuntimeError, AttributeError) as e:
                logging.warning("Failed to get module info of %s", module_id, exc_info=e)

        return None

    def get_display(self, module_version=None):
        if module_version:
            return self._get_module_model("Dx", "Display", module_version)

        for i in range(1, 40):
            module_id = "D%d" % i
            try:
                mm = self._get_module_model(module_id, "Display")
                if mm:
                    return mm
            except (RuntimeError, AttributeError) as e:
                logging.warning("Failed to get module info of %s", module_id, exc_info=e)

        return None

    def get_slave_power(self, module_version=None):
        if module_version:
            return self._get_module_model("Qx", "SlavePower", module_version)

        for i in range(1, 40):
            module_id = "Q%d" % i
            try:
                mm = self._get_module_model(module_id, "SlavePower")
                if mm:
                    return mm
            except (RuntimeError, AttributeError) as e:
                logging.warning("Failed to get module info of %s", module_id, exc_info=e)

        return None
