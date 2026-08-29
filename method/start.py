from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.jehova.Game import Game
from gdo.jehova.module_jehova import module_jehova


class start(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'jh.start'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_in_private(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        game = Game.instance(self._env_channel)
        if not game._inited:
            return self.err('err_jehova_no_game')
        if game._started:
            return self.err('err_jehova_running')
        if len(game._players) < 2:
            return self.err('err_jehova_at_least_two')
        game.start(music_duration=module_jehova.instance().cfg_music_duration())
        for player in game._players:
            player.increase_setting('jehova_started', 1)
        return self.msg('msg_jehova_started', (len(game._players),))
