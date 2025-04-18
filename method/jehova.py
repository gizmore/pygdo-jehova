from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.Connector import Connector
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_User import GDT_User
from gdo.jehova.Game import Game


class jehova(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'jehova'

    def gdo_connectors(self) -> str:
        return Connector.text_connectors()

    def gdo_in_private(self) -> bool:
        return False

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Repeat(GDT_User('players').same_channel()).not_null().min(2),
        ]

    def gdo_execute(self) -> GDT:
        game = Game.instance(self._env_channel)
        game.start(self.param_value('players'))
        return self.msg('msg_jehova_started', (len(game._players),))
