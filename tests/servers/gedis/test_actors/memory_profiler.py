from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from objgraph import count, show_most_common_types


class MemoryProfiler(BaseActor):
    @actor_method
    def object_count(self, object_type: str) -> int:
        """Gets number of object with type object_type in memory

        Arguments:
            object_type {str} -- object type

        Returns:
            int -- [description]
        """
        return count(object_type)

    @actor_method
    def print_top_types(self, limit: int) -> None:
        """Print top x object in memory

        Arguments:
            limit {int} -- max number of results
        """
        show_most_common_types(limit=int(limit))


Actor = MemoryProfiler
