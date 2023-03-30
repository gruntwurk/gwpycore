# The existence of this file makes this subfolder a "package"
__version__ = "0.0.5"

# The following imports make it so that the client only has to say
# "from gwpycore import X" where X is the ultimate class or function name

# flake8: noqa

# ############################################################################
#                                                                 CORE MODULES
# ############################################################################

from .core.logging import *
from .core.exceptions import *  # depends on logging
# Most of the following depend on exceptions, so we won't call that out
from .core.booleans import *
from .core.environ import *
from .core.strings import *
from .core.numeric import *
from .core.datetime_utils import *
from .core.colors import *
from .core.enums import *
from .core.keystrokes import *
from .core.typing_utils import *  # typing as in class types (not keystroke typing)
from .core.git import *
from .core.files import *  # depends on datetime
from .core.folders import *  # depends on files
from .core.cli import *  # depends on logging
from .core.config import *  # depends on booleans, strings, files, colors
from .core.installation import *  # depends on config

from .communications.email import *

from .gui.gui_theme import *

from .data.fuzzy import *
from .data.tree_node import *
from .data.dict_database import *
from .data.field_defs import *
from .data.csv_utils import *

from .images.images import *  # depends on files

from .lexical.words import *

if is_windows():
    from .windows.windows_fonts import *
    from .windows.windows_gui import *
    # from .windows.windows_behavior import *
    from .windows.windows_printing import *

from .testing_utils.logging_support import *

