from .size import VDC_SIZE
from .vdc import UserVDC
from jumpscale.clients.explorer.models import NextAction
from jumpscale.loader import j
from jumpscale.core.base import StoredFactory

VDC_INSTANCE_NAME_FORMAT = "vdc_{}_{}"


class VDCStoredFactory(StoredFactory):
    def new(self, vdc_name, owner_tname, flavor):
        if isinstance(flavor, VDC_SIZE.VDCFlavor):
            flavor = flavor.value
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        instance_name = VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        return super().new(instance_name, vdc_name=vdc_name, owner_tname=owner_tname, _flavor=flavor)

    def find(self, name=None, vdc_name=None, owner_tname=None, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot") if owner_tname else None
        instance_name = name or VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        instance = super().find(instance_name)
        if not instance:
            return
        if owner_tname and instance.owner_tname != owner_tname:
            return
        if load_info:
            instance.load_info()
        return instance

    def list(self, owner_tname, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        _, _, instances = self.find_many(owner_tname=owner_tname)
        if not load_info:
            return instances

        result = []
        for instance in instances:
            instance.load_info()
            result.append(instance)
        return result

    def from_dict(self, instance_dict):
        cp = instance_dict.copy()
        vdc_name = cp.pop("vdc_name")
        owner_tname = cp.pop("owner_tname")
        flavor = cp.pop("flavor")
        instance = self.new(vdc_name, owner_tname, flavor)
        for key, val in cp.items():
            setattr(instance, key, val)
        instance.save()
        return instance

    def delete(self, name):
        vdc = self.find(name)
        if vdc:
            # don't delete vdc wallets
            j.logger.info(f"Deleting vdc {vdc.vdc_name} with solution uuid: {vdc.solution_uuid}")
            self.cleanup_vdc(vdc)
        return super().delete(name)

    def cleanup_vdc(self, vdc):
        identity_instance_name = f"vdc_ident_{vdc.solution_uuid}"
        identity = j.core.identity.find(identity_instance_name)
        if identity:
            deployer = vdc.get_deployer(identity=identity)
            deployer.rollback_vdc_deployment()
            zos = j.sals.zos.get(identity_instance_name)
            for workload in zos.workloads.list(identity.tid, next_action=NextAction.DEPLOY):
                zos.workloads.decomission(workload.id)


VDCFACTORY = VDCStoredFactory(UserVDC)
VDCFACTORY.always_reload = True


def export_module_as():
    return VDCFACTORY
