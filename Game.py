from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_User import GDO_User


class Game:

    _users: list[GDO_User]
    _channel: GDO_Channel

    def __init__(self, channel: GDO_Channel):
        self._channel = channel

