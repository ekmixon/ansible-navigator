"""a couple singleton sentinels for convenience to avoid
use of None
"""

from typing import Any
from typing import Dict


class Singleton(type):
    """one of a kind"""

    _instances: Dict[Any, "Singleton"] = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class Unknown(metaclass=Singleton):
    # pylint: disable=too-few-public-methods
    """something that should eventually be known"""

    def __repr__(self):
        return type(self).__name__


unknown = Unknown()


class Nonexistent(metaclass=Singleton):
    # pylint: disable=too-few-public-methods
    """something that does not exist"""

    def __repr__(self):
        return type(self).__name__


nonexistent = Nonexistent()
