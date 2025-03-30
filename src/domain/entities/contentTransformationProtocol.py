import abc


class DataTransformationProtocol(abc.ABC):
    @abc.abstractmethod
    def direct_trasform(self, data: bytes) -> bytes:
        ...

    @abc.abstractmethod
    def reverse_transform(self, data: bytes) -> bytes:
        ...
