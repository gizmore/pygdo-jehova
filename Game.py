"""Per-channel state for Reise nach Jerusalem / Musical Chairs."""

from __future__ import annotations

from random import choice, randint

from gdo.base.Application import Application
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_User import GDO_User
from gdo.jehova.lyrics import next_lyrics, random_lyrics


class Game:

    GAMES: dict[str, 'Game'] = {}

    def __init__(self, channel: GDO_Channel):
        self._channel = channel
        self.reset()

    @classmethod
    def instance(cls, channel: GDO_Channel) -> 'Game':
        if game := cls.GAMES.get(channel.get_id()):
            return game
        game = cls(channel)
        cls.GAMES[channel.get_id()] = game
        return game

    def reset(self):
        self._players: list[GDO_User] = []
        self._initial_players = 0
        self._seats: dict[int, GDO_User] = {}
        self._inited = False
        self._started = False
        self._music = False
        self._round = 0
        self._broken_seat: int|None = None
        self._next_lyric = 0.0
        self._music_until = 0.0
        self._sit_until = 0.0
        self._lyrics: tuple[str, ...] = ()
        self._lyric_index = 0
        self._track = ''
        self._track_lyrics: tuple[str, ...] = ()
        self._track_finished = False

    def init(self, players: list[GDO_User]) -> 'Game':
        self.reset()
        self._inited = True
        # A connector command may rehydrate the same persisted user as a
        # different Python object than the object kept in channel._users.
        # Game membership is database identity, never object identity.
        self._players = list({player.get_id(): player for player in players}.values())
        self._initial_players = len(self._players)
        return self

    def join(self, player: GDO_User) -> bool:
        if self._is_player(player):
            return False
        self._players.append(player)
        return True

    def start(self, now: float|None = None, music_duration: float = 12.0) -> 'Game':
        self._started = True
        self._round = 1
        # A game keeps one song until it has played through.  The next round
        # after its final lines chooses a different track when available.
        self._track, self._track_lyrics = random_lyrics()
        self.begin_music(now, music_duration)
        return self

    def begin_music(self, now: float|None = None, music_duration: float = 12.0):
        now = Application.TIME if now is None else now
        self._music = True
        if self._track_finished:
            self._track, self._track_lyrics = random_lyrics(self._track)
            self._track_finished = False
        self._lyrics, self._track_finished = next_lyrics(
            self._channel, self._track, self._track_lyrics, randint(3, 6))
        self._lyric_index = 0
        self._seats = {}
        self._broken_seat = None
        self._next_lyric = now
        self._music_until = now + music_duration
        self._sit_until = 0.0

    def stop_music(self, now: float|None = None, sit_duration: float = 10.0) -> int:
        now = Application.TIME if now is None else now
        # Chairs remain numbered 1..N. A different random chair breaks each
        # round; the missing chair is not always simply the last one.
        self._broken_seat = choice(range(1, len(self._players) + 1))
        self._music = False
        self._sit_until = now + sit_duration
        return self._broken_seat

    def is_music_playing(self) -> bool:
        return self._started and self._music

    def is_sitting_time(self) -> bool:
        return self._started and not self._music and self._broken_seat is not None

    def available_seats(self) -> list[int]:
        if self._broken_seat is None:
            return []
        return [seat for seat in range(1, len(self._players) + 1)
                if seat != self._broken_seat and seat not in self._seats]

    def _is_player(self, player: GDO_User) -> bool:
        player_id = player.get_id()
        return any(current.get_id() == player_id for current in self._players)

    def _is_seated(self, player: GDO_User) -> bool:
        player_id = player.get_id()
        return any(current.get_id() == player_id for current in self._seats.values())

    def sit_down(self, player: GDO_User, seat: int) -> bool:
        if not self._is_player(player) or self._is_seated(player):
            return False
        if seat not in self.available_seats():
            return False
        self._seats[seat] = player
        return True

    def everyone_seated(self) -> bool:
        return len(self._seats) == len(self._players) - 1

    def resolve_round(self) -> tuple[list[GDO_User], GDO_User|None]:
        seated = list(self._seats.values())
        seated_ids = {player.get_id() for player in seated}
        eliminated = [player for player in self._players if player.get_id() not in seated_ids]
        self._players = [player for player in self._players if player.get_id() in seated_ids]
        self._seats = {}
        self._broken_seat = None
        if len(self._players) <= 1:
            self._started = False
            self._music = False
            return eliminated, self._players[0] if self._players else None
        self._round += 1
        return eliminated, None

    def points_for_eliminated(self, eliminated: list[GDO_User]) -> list[tuple[GDO_User, int]]:
        """Return the final-table points for players eliminated this round."""
        survivors = len(self._players)
        total = self._initial_players
        return [
            (player, max(0, total - (survivors + len(eliminated) - index)))
            for index, player in enumerate(eliminated)
        ]

    def winner_points(self) -> int:
        return max(0, self._initial_players - 1)

    def tick(self, now: float, music_interval: float|tuple[float, float], sit_duration: float) -> tuple[str, object]|None:
        if not self._started:
            return None
        if self._music:
            if now >= self._music_until or self._lyric_index >= len(self._lyrics):
                return 'stop', self.stop_music(now, sit_duration)
            if now >= self._next_lyric:
                if isinstance(music_interval, tuple):
                    interval = randint(round(music_interval[0]), round(music_interval[1]))
                else:
                    interval = music_interval
                self._next_lyric = now + interval
                lyric = self._lyrics[self._lyric_index % len(self._lyrics)]
                self._lyric_index += 1
                return 'lyric', lyric
        elif now >= self._sit_until or self.everyone_seated():
            return 'resolved', self.resolve_round()
        return None
