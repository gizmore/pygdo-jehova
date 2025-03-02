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
