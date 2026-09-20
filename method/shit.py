"""A memorable alias for selecting a Musical Chairs seat."""

from gdo.jehova.method.sit import sit


class shit(sit):
    """``$shit <chair>`` is short for jeHova SIT."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'shit'

