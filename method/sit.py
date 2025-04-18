from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_UInt import GDT_UInt
from gdo.jehova.Game import Game


class sit(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'seat'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UInt('seat').not_null().min(1)
        ]

    def gdo_execute(self) -> GDT:
        seat = self.param_value('seat')
        game = Game.instance(self._env_channel)
        if game.is_music_playing():
            self.error('err_jehova_still_music')
        if not game.has_seat(seat):
            self.error('err_jehova_no_seat')
        elif game.sit_down(self._env_user, seat):
            self.msg('msg_jehova_sat_down')
        else:
            self.error('err_jehova_seat_taken')
        if game.has_ended():
            self.msg('msg_jehova_game_over')
