from jumpscale.core.exceptions import Input
from jumpscale.clients.explorer.models import Volume, DiskType, ContainerMount, WorkloadType, Container


class VolumesGenerator:
    """ """

    def create(self, node_id: str, pool_id: int, size: int = 5, type=DiskType.HDD) -> Volume:
        """add a volume to the reservation

        Args:
          node_id(str): id of the node where to reserve the volume
          pool_id(int) the capacity pool ID
          size(int, optional): size in GiB. Defaults to 5.
          type(str, optional): type of disk to use. Can be SSD or HDD. Defaults to "HDD".

        Returns:
          Volume: the newly created volume object
        """

        volume = Volume()
        volume.size = size
        volume.type = type
        volume.info.node_id = node_id
        volume.info.pool_id = pool_id
        volume.info.workload_type = WorkloadType.Volume
        return volume

    def attach_existing(self, container: Container, volume_id: str, mount_point: str):
        """attach an existing volume to a container.
           The volume must already exist on the node

        Args:
          container(Volume): container object returned from container.create_container function
          volume_id(str): the complete volume ID, format should be '{reservation.id}-{volume.workload_id}'
          mount_point(str): path where to mount the volume in the container
        """
        vol = ContainerMount()
        vol.volume_id = volume_id
        vol.mountpoint = mount_point
        container.volumes.append(vol)
