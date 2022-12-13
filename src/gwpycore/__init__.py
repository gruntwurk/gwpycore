# The existence of this file makes this subfolder a "package"
__version__ = "0.0.5"

# The following imports make it so that the client only has to say
# "from gwpycore import X" where X is the ultimate class or function name

# flake8: noqa


# ############################################################################
#                                                                 CORE MODULES
# ############################################################################

from .core.gw_logging import *
from .core.gw_exceptions import *  # depends on gw_logging
# Most of the following depend on gw_exceptions, so we won't call that out,
# specifically, in the comments below.
from .core.booleans import *
from .core.environ import *
from .core.gw_strings import *
from .core.gw_numeric import *
from .core.gw_datetime import *
from .core.gw_colors import *
from .core.keystrokes import *
from .core.gw_typing import *
from .core.gw_versioning import *
from .core.gw_files import *  # depends on gw_datetime
from .core.gw_cli import *  # depends on gw_logging
from .core.gw_config import *  # depends on booleans, gw_strings, gw_files, gw_colors

from .gui.gw_gui_theme import *

from .data.gw_fuzzy import *
from .data.gw_tree_node import *
from .data.dict_database import *
from .data.csv_utils import *

from .images.images import *  # depends on gw_files

from .lexical.words import *

if is_windows():
    from .windows.gw_windows_fonts import *
    from .windows.gw_windows_gui import *
    # from .windows.gw_windows_behavior import *
    from .windows.gw_windows_printing import *

from .video.gw_cameras import *

from .testing_utils.logging_support import *


# ############################################################################
#                                                        Optional KIVY MODULES
# ############################################################################
# "Optional" means that this code is included, but in order to use any of it,
# The optional `kivy` dependencies must be installed, e.g.
#     pip install gypycore[kivy]

if is_module_installed('kivy'):
    from .kivy.app_support.dialogs import *
    from .kivy.app_support.screens import *
    from .kivy.app_support.main_window import *
    from .kivy.system_support.kivy_exceptions import *
    from .kivy.widgets.background import *
    from .kivy.widgets.camera import *
    from .kivy.widgets.dropdown import *
    from .kivy.widgets.crop_tool import *
    from .kivy.widgets.screen_widget import *
    from .kivy.widgets.scroll_widget import *
    from .kivy.widgets.label import *
    from .kivy.widgets.button import *
    from .kivy.widgets.hotkey import *
    # from .kivy.assets.fonts import *
    # from .kivy.assets.icons import *
    # from .kivy.assets.images import *
    # from .kivy.assets.key_map import *
    # from .kivy.assets.skins import *
    # from .kivy.assets.svg import *
    # from .kivy.assets.syntax import *


# ############################################################################
#                                                   Optional REPORTLAB MODULES
# ############################################################################
# "Optional" means that this code is included, but in order to use any of it,
# The optional `reportlab` dependencies must be installed, e.g.
#     pip install gypycore[reportlab]

if is_module_installed('reportlab'):
    from .reportlab.gw_rl_fonts import *
    from .reportlab.flowables.text_flowables import *
    from .reportlab.templates.multi_column import *
    from .reportlab.templates.id_badge import *

