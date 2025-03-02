from gdo.base.Cache import Cache
from gdo.base.WithSerialization import WithSerialization
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_User import GDO_User


class Game(WithSerialization):

    _users: list[GDO_User]
    _channel: GDO_Channel

    def __init__(self, channel: GDO_Channel):
        self._channel = channel

    @classmethod
    def instance(cls, channel: GDO_Channel):
        if game := Cache.get('jhv_game', channel.get_id()):
            return game
        game = cls(channel)
        Cache.set('jhv_game', channel.get_id(), game)
        return game

