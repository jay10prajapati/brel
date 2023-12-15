from lxml import etree
from brel.parsers.dts import IFileManager
import validators

class SchemaResolver(etree.Resolver):
    def __init__(self, schema_manager: IFileManager) -> None:
        self.__schema_manager = schema_manager
    
    def resolve(self, system_url: str, public_id: str):
        print (f"Resolving {system_url}")
        print (f"Public ID: {public_id}")
        return super().resolve(system_url, public_id)
