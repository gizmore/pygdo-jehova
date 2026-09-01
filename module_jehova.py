from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_Bool import GDT_Bool
from gdo.date.GDT_Duration import GDT_Duration
from gdo.jehova.Game import Game
from random import randint


class module_jehova(GDO_Module):

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('music_duration').not_null().min(6).initial('60s'),
            GDT_Duration('music_interval_min').not_null().min(1).initial('6s'),
            GDT_Duration('music_interval_max').not_null().min(1).initial('9s'),
            GDT_Duration('sit_duration').not_null().min(3).initial('10s'),
        ]

    def cfg_music_duration(self) -> float:
        return self.get_config_value('music_duration')

    def cfg_music_interval(self) -> tuple[float, float]:
        return (
            self.get_config_value('music_interval_min'),
            self.get_config_value('music_interval_max'),
        )

    def cfg_sit_duration(self) -> float:
        return self.get_config_value('sit_duration')

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_UInt('jehova_started').initial('0'),
            GDT_UInt('jehova_won').initial('0'),
            GDT_UInt('jehova_points').initial('0'),
        ]

    def gdo_user_settings(self) -> list[GDT]:
        # Players are opted in by default.  This stays a normal writable
        # setting so `$set jehova 0` excludes a user from future rounds.
        return [
            GDT_Bool('jehova').not_null().initial('1'),
        ]

    def gdo_subscribe_events(self):
        Application.EVENTS.add_timer_async(1, self.jehova_timer, Application.EVENTS.FOREVER)

    async def start_game(self, game: Game) -> bool:
        if len(game._players) < 2:
            game.reset()
            await game._channel.send(t('err_jehova_at_least_two'))
            return False
        game.start(music_duration=self.cfg_music_duration())
        for player in game._players:
            player.increase_setting('jehova_started', 1)
        await game._channel.send(t('msg_jehova_started', (len(game._players),)))
        return True

    async def jehova_timer(self):
        for game in list(Game.GAMES.values()):
            event = game.tick(Application.TIME, self.cfg_music_interval(), self.cfg_sit_duration())
            if event is None:
                continue
            kind, value = event
            if kind == 'lyric':
                await game._channel.send(value)
            elif kind == 'stop':
                await game._channel.send(t('msg_jehova_stop', (value, self.cfg_sit_duration())))
            else:
                eliminated, winner = value
                for player, points in game.points_for_eliminated(eliminated):
                    if points:
                        player.increase_setting('jehova_points', points)
                if winner:
                    winner.increase_setting('jehova_won', 1)
                    winner.increase_setting('jehova_points', game.winner_points())
                    await game._channel.send(t('msg_jehova_winner', (winner.render_name(),)))
                elif game._started:
                    players = ', '.join(player.render_name() for player in game._players)
                    await game._channel.send(t('msg_jehova_next_players', (players,)))
                    game.begin_music(Application.TIME, self.cfg_music_duration())
                    await game._channel.send(t('msg_jehova_next_round', (game._round, len(game._players))))
                else:
                    await game._channel.send(t(f'msg_jehove_oh_noe_winner_{randint(1, 4)}'))
