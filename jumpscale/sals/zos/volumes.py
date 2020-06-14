from .id import _next_workload_id
from jumpscale.core.exceptions import Input
from jumpscale.clients.explorer.models import (
    TfgridWorkloadsReservationVolume1,
    DiskType,
    TfgridWorkloadsReservationContainerMount1,
)


class Volumes:
    def create(self, reservation, node_id, size=5, type=DiskType.HDD):
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

        volume = TfgridWorkloadsReservationVolume1()
        volume.workload_id = _next_workload_id(reservation)
        volume.size = size
        volume.type = type
        volume.node_id = node_id
        reservation.data_reservation.volumes.append(volume)
        return volume

    def attach(self, container, volume, mount_point):
        """attach a volume to a container.
           The volume must be defined in the same reservation

        Args:
            container ([type]): container object from create_container function
            volume ([type]): Volume object that is returned from add_volume function
            mount_point (str): path where to mount the volume in the container
        """
        vol = TfgridWorkloadsReservationContainerMount1()
        vol.volume_id = f"-{volume.workload_id}"
        vol.mountpoint = mount_point
        container.volumes.append(vol)

    def attach_existing(self, container, volume_id, mount_point):
        """attach an existing volume to a container.
           The volume must already exist on the node

        Args:
            container ([type]): container object returned from container.create_container function
            volume_id ([type]): the complete volume ID, format should be '{reservation.id}-{volume.workload_id}'
            mount_point (str): path where to mount the volume in the container
        """
        vol = TfgridWorkloadsReservationContainerMount1()
        vol.volume_id = volume_id
        vol.mountpoint = mount_point
        container.volumes.append(vol)
