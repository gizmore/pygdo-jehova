from gdo.base.Cache import Cache
from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_User import GDO_User
from gdo.jehova.lyrics import lyrics


class Game(WithSerialization):

    _players: list[GDO_User]
    _channel: GDO_Channel
    _seats: list[GDO_User]
    _started: bool
    _playing: bool
    _lyrics: str
    _line: int

    def __init__(self, channel: GDO_Channel):
        self._players = []
        self._channel = channel
        self._seats = []
        self._started = False
        self._lyrics = lyrics.LYRICS.keys()[0]
        self._line = 0

    @classmethod
    def instance(cls, channel: GDO_Channel) -> 'Game':
        if game := Cache.get('jhv_game', channel.get_id()):
            return game
        game = cls(channel)
        Cache.set('jhv_game', channel.get_id(), game)
        return game

    def start(self, players: list[GDO_User]) -> 'Game':
        self._players = players
        self._started = True
        self._playing = True
        return self

    def has_ended(self) -> bool:
        pass
