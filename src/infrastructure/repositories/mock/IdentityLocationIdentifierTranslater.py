from domain.entities.locationIdentifierTranslater import LocationIdentifierTranslater


class IdentityLocationIdentifierTranslater(LocationIdentifierTranslater):
    def translate(self, location_id: str) -> str:
        return location_id
