import abc

class LocationIdentifierTranslater(abc.ABC):
    @abc.abstractmethod
    def translate(self, location_id: str) -> str:
        ...
