from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_UInt import GDT_UInt
from gdo.jehova import Game


class sit(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UInt('seat').not_null()
        ]

    def gdo_execute(self) -> GDT:
        seat = self.param_value('seat')
        game = Game.instance(self._env_channel)

