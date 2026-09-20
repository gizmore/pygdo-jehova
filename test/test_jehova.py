import os
import unittest
from unittest.mock import patch

from gdo.base.Application import Application
from gdo.base.Trans import t
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.connector.Bash import Bash
from gdo.core.GDO_Method import GDO_Method
from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
from gdo.core.GDT_UserType import GDT_UserType
from gdo.jehova.Game import Game
from gdo.jehova.lyrics import LYRICS, next_lyrics
from gdo.jehova.method.jehova import jehova
from gdo.jehova.method.shit import shit
from gdotest.TestUtil import GDOTestCase, cli_gizmore, cli_plug, cli_user, reinstall_module


class JehovaTest(GDOTestCase):

    def setUp(self):
        super().setUp()
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        reinstall_module('jehova')
        loader.init_modules(True, True)
        Application.init_cli()
        loader.init_cli()

    def test_01_random_broken_chair_and_five_second_timeout(self):
        channel = Bash.get_server().get_or_create_channel('jehova_game_test')
        game = Game.instance(channel)
        gizmore = cli_gizmore()
        peter = cli_user('jehova_peter')
        paul = cli_user('jehova_paul')
        game.init([gizmore, peter, paul])
        game.start(now=100, music_duration=1)

        self.assertEqual('lyric', game.tick(100, 1, 5)[0])
        with patch('gdo.jehova.Game.choice', return_value=2):
            kind, broken = game.tick(101, 1, 5)
        self.assertEqual('stop', kind)
        self.assertEqual(2, broken)
        self.assertEqual([1, 3], game.available_seats())
        self.assertTrue(game.sit_down(gizmore, 1))
        self.assertFalse(game.sit_down(peter, 2))
        self.assertTrue(game.sit_down(peter, 3))
        kind, (eliminated, winner) = game.tick(102, 1, 5)
        self.assertEqual('resolved', kind)
        self.assertEqual([paul], eliminated)
        self.assertIsNone(winner)
        self.assertEqual(2, len(game._players))
        self.assertEqual([gizmore, peter], game._players)
        self.assertEqual([(paul, 0)], game.points_for_eliminated(eliminated))

        # If nobody sits down, the game ends instead of starting an empty
        # follow-up round.
        game.init([gizmore, peter])
        game._started = True
        game._players = []
        _, winner = game.resolve_round()
        self.assertIsNone(winner)
        self.assertFalse(game._inited)
        self.assertFalse(game._started)

    def test_02_main_command_starts_the_game(self):
        self.assertEqual('jehova', jehova.gdo_trigger())
        self.assertEqual('jh', jehova.gdo_trig())
        self.assertEqual('shit', shit.gdo_trigger())
        self.assertEqual('shit', shit.gdo_trig())
        self.assertIsNotNone(GDO_Method.get_by_name('jehova.shit'))

    def test_03_plays_one_selected_lyric_track_in_order(self):
        channel = Bash.get_server().get_or_create_channel('jehova_lyrics_test')
        game = Game.instance(channel)
        game.init([cli_gizmore()])
        with patch('gdo.jehova.Game.random_lyrics', return_value=('test', ('first', 'second', 'third'))), \
             patch('gdo.jehova.Game.randint', return_value=3):
            game.start(now=100, music_duration=10)
        self.assertEqual(('lyric', 'first'), game.tick(100, 1, 5))
        self.assertEqual(('lyric', 'second'), game.tick(101, 1, 5))
        self.assertEqual(('lyric', 'third'), game.tick(102, 1, 5))
        self.assertEqual('stop', game.tick(103, 1, 5)[0])

        # No playlist directory is required for a playable fresh install.
        self.assertTrue(LYRICS)

    def test_04_keeps_the_same_track_until_it_has_ended(self):
        channel = Bash.get_server().get_or_create_channel('jehova_same_track_test')
        game = Game.instance(channel)
        game.init([cli_gizmore()])
        with patch('gdo.jehova.Game.random_lyrics', return_value=('track', ('a', 'b', 'c', 'd', 'e', 'f'))) as select, \
             patch('gdo.jehova.Game.randint', return_value=3):
            game.start(now=100, music_duration=10)
            game.begin_music(now=200, music_duration=10)
        select.assert_called_once()

    def test_04b_music_interval_is_random_in_the_configured_range(self):
        channel = Bash.get_server().get_or_create_channel('jehova_interval_test')
        game = Game.instance(channel).init([cli_gizmore()])
        game._started = game._music = True
        game._lyrics = ('first', 'second')
        game._music_until = 100
        with patch('gdo.jehova.Game.randint', return_value=8):
            self.assertEqual(('lyric', 'first'), game.tick(10, (6, 9), 5))
        self.assertEqual(18, game._next_lyric)

    def test_04c_music_waits_for_the_configured_minimum_messages(self):
        channel = Bash.get_server().get_or_create_channel('jehova_min_messages_test')
        game = Game.instance(channel).init([cli_gizmore()])
        with patch('gdo.jehova.Game.random_lyrics', return_value=('test', ('first', 'second'))):
            game.start(now=100, music_duration=0, min_messages=1)
        self.assertEqual(('lyric', 'first'), game.tick(100, 1, 5))
        self.assertEqual('stop', game.tick(101, 1, 5)[0])

    def test_05_track_cursor_is_stored_per_channel_and_filename(self):
        first = Bash.get_server().get_or_create_channel('jehova_track_first')
        second = Bash.get_server().get_or_create_channel('jehova_track_second')
        method = GDO_Method.get_by_name('jehova.jehova')
        for channel in (first, second):
            GDO_MethodValChannel.table().delete_by_id(method.get_id(), channel.get_id(), 'mentor.nf0')
        lines = ('a', 'b', 'c')
        self.assertEqual((('a', 'b'), False), next_lyrics(first, 'mentor.nf0', lines, 2))
        self.assertEqual((('c',), True), next_lyrics(first, 'mentor.nf0', lines, 2))
        self.assertEqual((('a', 'b'), False), next_lyrics(second, 'mentor.nf0', lines, 2))

    def test_06_channel_commands_start_all_non_bot_users(self):
        channel = Bash.get_server().get_or_create_channel('jehova_everyone_test')
        gizmore = cli_gizmore()
        peter = cli_user('jehova_command_peter')
        service = cli_user('jehova_chanserv')
        gpt = cli_user('jehova_gpt')
        service.save_val('user_type', GDT_UserType.BOT)
        gpt.save_val('user_type', GDT_UserType.CHAPPY)
        channel._users = {
            gizmore.get_name(): gizmore,
            peter.get_name(): peter,
            service.get_name(): service,
            gpt.get_name(): gpt,
        }
        game = Game.instance(channel)
        game.init([user for user in channel._users.values() if jehova.can_play(user)])
        self.assertEqual([gizmore, peter, gpt], game._players)

    def test_07_points_follow_final_table_position(self):
        channel = Bash.get_server().get_or_create_channel('jehova_points_test')
        players = [cli_user(f'jehova_points_{index}') for index in range(4)]
        game = Game.instance(channel).init(players)
        game._players = players[:2]
        self.assertEqual([(players[2], 0), (players[3], 1)],
                         game.points_for_eliminated(players[2:]))
        self.assertEqual(3, game.winner_points())

    def test_08_has_all_no_winner_taunts(self):
        for index in range(1, 5):
            key = f'msg_jehove_oh_noe_winner_{index}'
            self.assertNotEqual(key, t(key))


if __name__ == '__main__':
    unittest.main()
