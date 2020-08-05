from .id import _next_workload_id
from jumpscale.core.exceptions import Input
from jumpscale.clients.explorer.models import (
    Volume,
    DiskType,
    ContainerMount,
    WorkloadType,
)


class VolumesGenerator:
    def create(self, node_id, pool_id, size=5, type=DiskType.HDD):
        """add a volume to the reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation to add the volume to
            node_id (str): id of the node where to reserve the volume
            size (int, optional): size in GiB. Defaults to 5.
            type (str, optional): type of disk to use. Can be SSD or HDD. Defaults to "HDD".

        Raises:
            jumpscale.core.exceptions.Input: If type is not supported

        Returns:
            [type]: the newly created volume object
        """

        volume = Volume()
        volume.size = size
        volume.type = type
        volume.info.node_id = node_id
        volume.info.pool_id = pool_id
        volume.info.workload_type = WorkloadType.Volume
        return volume

    def attach_existing(self, container, volume_id, mount_point):
        """attach an existing volume to a container.
           The volume must already exist on the node

        Args:
            container ([type]): container object returned from container.create_container function
            volume_id ([type]): the complete volume ID, format should be '{reservation.id}-{volume.workload_id}'
            mount_point (str): path where to mount the volume in the container
        """
        vol = ContainerMount()
        vol.volume_id = volume_id
        vol.mountpoint = mount_point
        container.volumes.append(vol)
