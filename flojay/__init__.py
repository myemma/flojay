"""Flojay json streaming module.

For more information, see: http://github.com/myemma/flojay/
"""

# the Canonical way ;)
version_info = (0, 1, 0, 'alpha', 0)

__version__ = '.'.join(str(i) for i in version_info[0:3])
version_string = __version__

from flojay_extension import *
