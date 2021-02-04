from pymine.types.chunk import Chunk


class AbstractWorldGenerator:
    """Abstract class used to create a world generator."""

    @staticmethod
    def generate_chunk(seed: int, chunk_x: int, chunk_z: int) -> Chunk:
        raise NotImplementedError(self.__class__.__name__)


class AbstractChunkIO:
    """Abstract class used to create chunk io."""

    @staticmethod
    def calc_offset(chunk_x: int, chunk_z: int) -> int:
        raise NotImplementedError

    @staticmethod
    def find_chunk(location: int) -> tuple:
        raise NotImplementedError

    @classmethod
    def fetch_chunk(cls, world_path: str, chunk_x: int, chunk_z: int) -> Chunk:
        raise NotImplementedError(cls.__class__.__name__)

    @classmethod
    async def fetch_chunk_async(cls, world_path: str, chunk_x: int, chunk_z: int) -> Chunk:
        raise NotImplementedError(cls.__class__.__name__)
