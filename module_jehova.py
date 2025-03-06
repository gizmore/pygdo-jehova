from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDT_UInt import GDT_UInt


class module_jehova(GDO_Module):

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_UInt('jehova_started').initial('0'),
            GDT_UInt('jehova_played').initial('0'),
            GDT_UInt('jehova_lost').initial('0'),
        ]

    def gdo_init(self):
        pass

    def gdo_subscribe_events(self):
        Application.EVENTS.add_timer(10, self.jehova_timer, Application.EVENTS.FOREVER)

    def jehova_timer(self):
        pass
