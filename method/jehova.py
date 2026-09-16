from gdo.base.GDT import GDT
from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.core.GDT_UserType import GDT_UserType
from gdo.jehova.Game import Game
from gdo.jehova.module_jehova import module_jehova
from random import randint


class jehova(Method):

    @staticmethod
    def can_play(user) -> bool:
        """Service bots stay visible in a channel, but do not take chairs."""
        return user.get_user_type() != GDT_UserType.BOT

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'jehova'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'jh'

    def gdo_in_private(self) -> bool:
        return False

    def gdo_execute(self) -> GDT:
        game = Game.instance(self._env_channel)
        if game._inited:
            return self.err('err_jehova_running')
        players = [
            user for user in self._env_channel._users.values()
            if self.can_play(user)
        ]
        game.init(players)
        delay = randint(3, 6)

        async def start_game():
            # A stopped/replaced round must not be revived by its old timer.
            if game._inited and not game._started:
                await module_jehova.instance().start_game(game)

        Application.EVENTS.add_timer_async(delay, start_game)
        return self.msg('msg_jehova_inited', (delay,))
