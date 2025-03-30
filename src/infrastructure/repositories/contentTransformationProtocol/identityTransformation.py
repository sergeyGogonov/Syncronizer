from domain.entities.contentTransformationProtocol import DataTransformationProtocol 


class IdentityTransformationProtocol(DataTransformationProtocol):
    def direct_trasform(self, data: bytes) -> bytes:
        return data


    def reverse_transform(self, data: bytes) -> bytes:
        return data
