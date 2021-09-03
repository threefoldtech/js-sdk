import math

from jumpscale.loader import j

from jumpscale.clients.explorer.models import DiskType

from .s3_auto_topup import extend_zdbs, get_farm_pool_id, get_zdb_farms_distribution


class ZDBMonitor:
    def __init__(self, vdc_instance) -> None:
        self.vdc_instance = vdc_instance

    @property
    def zdbs(self):
        if not self.vdc_instance.s3.zdbs:
            self.vdc_instance.load_info()
        return self.vdc_instance.s3.zdbs

    @property
    def zdb_total_size(self):
        size = 0
        for zdb in self.zdbs:
            size += zdb.size
        return size

    def is_extend_triggered(self, threshold=0.7, limit=None):
        """
        check if zdbs need to be extended according to threshold (0.7) and maximum limit in GB if specified
        """
        util = self.check_utilization()
        if util < threshold:
            return False, util
        if limit and self.zdb_total_size >= limit:
            return False, util
        return True, util

    def get_zdbs_usage(self):
        zdbs_usage = {}
        for zdb in self.zdbs:
            client = j.clients.redis.get(f"zdb_{zdb.wid}")
            client.hostname = zdb.ip_address
            client.port = zdb.port
            try:
                result = client.execute_command("nsinfo", zdb.namespace)
            except Exception as e:
                j.logger.error(f"failed to fetch namespace info for zdb: {zdb} due to error {str(e)}")
                continue
            nsinfo = self._parse_info(result.decode())
            if not all(["data_size_bytes" in nsinfo, "data_limits_bytes" in nsinfo]):
                j.logger.warning(f"missing data_size and data_limits keys in namespace info for zdb: {zdb}")
                continue
            zdbs_usage[zdb.wid] = float(nsinfo["data_size_bytes"]) / 1024 ** 3 / zdb.size
        return zdbs_usage

    def check_utilization(self):
        """
        connect to all zdbs and check data utilization
        """
        total_usage = 0
        for usage in self.get_zdbs_usage().values():
            total_usage += usage
        return total_usage

    def _parse_info(self, info: str):
        result = {}
        for line in info.splitlines():
            splits = line.split(": ")
            if len(splits) != 2:
                continue
            key, val = splits[0], splits[1]
            result[key] = val
        return result

    def get_extension_capacity(self, threshold=0.7, clear_threshold=0.4, limit=None):
        triggered, util = self.is_extend_triggered(threshold, limit)
        j.logger.info(f"zdbs current utilization: {util} extension triggered: {triggered}")
        if not triggered:
            return 0
        total_storage = self.zdb_total_size
        used_storage = util * total_storage
        required_capacity = (used_storage / clear_threshold) - total_storage
        j.logger.info(
            f"zdb stats: total_storage: {total_storage}, used_storage: {used_storage}, required_capacity: {required_capacity}, limit: {limit}, clear_threshold: {clear_threshold}"
        )
        if limit and required_capacity + used_storage > limit:
            required_capacity = limit - used_storage

        if required_capacity < 1:
            return 0

        return required_capacity

    def get_password(self, identity=None):
        identity = identity or self.vdc_instance._get_identity()
        zos = j.sals.zos.get(identity.instance_name)
        for zdb in self.zdbs:
            workload = zos.workloads.get(zdb.wid)
            metadata = j.sals.reservation_chatflow.deployer.decrypt_metadata(
                workload.info.metadata, identity.instance_name
            )
            try:
                metadata_dict = j.data.serializers.json.loads(metadata)
            except Exception as e:
                continue
            if not metadata_dict.get("password"):
                continue
            return metadata_dict["password"]
        else:
            password = self.vdc_instance.get_password()
            if password:
                return password
        raise j.exceptions.Runtime("Couldn't get password for any zdb of vdc")

    def extend(
        self,
        required_capacity,
        farm_names,
        wallet_name="provision_wallet",
        extension_size=10,
        nodes_ids=None,
        duration=None,
        disk_type=DiskType.HDD,
    ):
        if not duration:
            duration = self.vdc_instance.get_pools_expiration() - j.data.time.utcnow().timestamp
            two_weeks = 2 * 7 * 24 * 60 * 60
            duration = duration if duration < two_weeks else two_weeks
        password = self.get_password()
        no_zdbs = math.ceil(required_capacity / extension_size)
        if no_zdbs < 1:
            return
        solution_uuid = self.vdc_instance.solution_uuid
        farm_names = get_zdb_farms_distribution(solution_uuid, farm_names, no_zdbs)
        pool_ids = []
        farm_pools = {}
        for farm_name in farm_names:
            pool_id = farm_pools.get(farm_name)
            if not pool_id:
                pool_id = get_farm_pool_id(farm_name)
                farm_pools[farm_name] = pool_id
            pool_ids.append(pool_id)
        wallet = getattr(self.vdc_instance, wallet_name)
        wids, _ = extend_zdbs(
            self.vdc_instance.vdc_name,
            pool_ids,
            solution_uuid,
            password,
            duration,
            extension_size,
            wallet_name=wallet.instance_name,
            nodes_ids=nodes_ids,
            disk_type=disk_type,
        )
        j.logger.info(f"zdbs extended with wids: {wids}")
        if len(wids) != no_zdbs:
            j.logger.error(f"AUTO_TOPUP: Couldn't deploy all required zdbs. successful workloads {wids}")
        return wids
