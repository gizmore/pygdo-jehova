from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_UInt import GDT_UInt
from gdo.jehova.Game import Game


class sit(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'jh.sit'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_in_private(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_UInt('seat').not_null().min(1).positional()]

    async def gdo_execute(self) -> GDT:
        game = Game.instance(self._env_channel)
        if not game._started:
            return self.err('err_jehova_no_game')
        if game.is_music_playing():
            return self.err('err_jehova_still_music')
        if not game.is_sitting_time():
            return self.err('err_jehova_no_seat')
        seat = self.param_value('seat')
        if not game.sit_down(self._env_user, seat):
            return self.err('err_jehova_seat_taken')
        if game.everyone_seated():
            # Resolve immediately for the last successful player.
            from gdo.jehova.module_jehova import module_jehova
            await module_jehova.instance().jehova_timer()
        return self.msg('msg_jehova_sat_down', (seat,))
