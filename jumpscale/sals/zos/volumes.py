from jumpscale.core.exceptions import Input
from jumpscale.clients.explorer.models import Volume, DiskType, ContainerMount, WorkloadType, Container
from typing import Union


class VolumesGenerator:
    """ """

    def create(self, node_id: str, pool_id: int, size: int = 5, type: Union[str, DiskType] = DiskType.HDD) -> Volume:
        """add a volume to the reservation

        Args:
          node_id(str): id of the node where to reserve the volume
          pool_id(int) the capacity pool ID
          size(int, optional): size in GiB. Defaults to 5.
          type(Union[str,DiskType], optional): type of disk to use. Can be SSD or HDD. Defaults to "HDD".

        Returns:
          Volume: the newly created volume object
        """
        if isinstance(type, str):
            type = getattr(DiskType, type)

        volume = Volume()
        volume.size = size
        volume.type = type
        volume.info.node_id = node_id
        volume.info.pool_id = pool_id
        volume.info.workload_type = WorkloadType.Volume
        return volume

    def attach_existing(self, container: Container, volume_id: Union[str, Volume], mount_point: str):
        """attach an existing volume to a container.
           The volume must already exist on the node

        Args:
          container(Volume): container object returned from container.create_container function
          volume_id(Union[str,volume]): the volume to attached to the container or its full ID
          mount_point(str): path where to mount the volume in the container
        """
        if isinstance(volume_id, Volume):
            if not volume_id.id:
                raise Input("volume needs to be deployed before it can be attached to a container")
            volume_id = f"{volume_id.id}-1"

        vol = ContainerMount()
        vol.volume_id = volume_id
        vol.mountpoint = mount_point
        container.volumes.append(vol)
