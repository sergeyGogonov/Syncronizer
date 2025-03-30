from pathlib import Path
from domain.interfaces.gateway.gatewayFactory import GatewayFactory


class OsGatewayFactory(GatewayFactory):
    def __init__(
        self,
        abs_root_dir_path: str
    ):
        self._root_dir_path = Path(abs_root_dir_path.rstrip('/') + '/')
        self._check_root_path()
        
    def _check_root_path(self): 
        if not self._root_dir_path.is_absolute():
            raise ValueError(
                'Передан не абсолютный путь!'
                f'root_dir_path={str(self._root_dir_path)}'
            )

    def get_readable_gateway(
        self,
        location_protocol: 'LocationIdentifierProtocol | None' = None
    ) -> 'ReadableGateway':
        ...

    def get_preserving_gateway(
        self,
        location_protocol: 'LocationIdentifierProtocol | None' = None
    ) -> 'PreservingGateway':
        ...
    
    def get_deleting_gateway(
        self,
        location_protocol: 'LocationIdentifierProtocol | None' = None
    ) -> 'DeletingGateway':
        ... 
