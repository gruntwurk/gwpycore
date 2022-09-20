# The existence of this file makes this subfolder a "package"
__version__ = "0.0.5"

# The following imports make it so that the client only has to say
# "from gwpycore import X" where X is the ultimate class or function name

# flake8: noqa


# ############################################################################
#                                                                 CORE MODULES
# ############################################################################
from .core.gw_cli import *
from .core.gw_colors import *
from .core.gw_config import *
from .core.gw_datetime import *
from .core.gw_exceptions import *
from .core.gw_files import *
from .core.gw_images import *
from .core.gw_logging import *
from .core.gw_numeric import *
from .core.gw_strings import *
from .core.gw_typing import *
from .core.gw_versioning import *
from .core.gw_words import *

from .gui.gw_gui_theme import *

# from .data.gw_fuzzy import *
# from .data.gw_tree_node import *
from .data.dict_database import *

# from .gw_functions.gw_alphabet import * # TODO move this to a separate HamRadio project

# from .windows.gw_windows_fonts import *
from .windows.gw_windows_gui import *
# from .windows.gw_windows_behavior import *
# from .windows.gw_windows_printing import *

from .video.gw_cameras import *


# ############################################################################
#                                                        Optional KIVY MODULES
# ############################################################################
# "Optional" means that this code is included, but in order to use any of it,
# The optional `kivy` dependencies must be installed, e.g.
#     pip install gypycore[kivy]

from .kivy.app_support.dialogs import *
from .kivy.app_support.screens import *
from .kivy.app_support.main_window import *
from .kivy.system_support.kivy_exceptions import *
from .kivy.widgets.background import *
from .kivy.widgets.camera import *
from .kivy.widgets.dropdown import *
from .kivy.widgets.crop_tool import *
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

from .reportlab.gw_rl_fonts import *