from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Connector import Connector


class jehova(Method):

    def gdo_trigger(self) -> str:
        return 'jehova'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_in_private(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        pass
