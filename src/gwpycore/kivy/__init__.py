# The existence of this file makes this subfolder a "package"

# The following imports make it so that the client only has to say
# "from gwpycore.kivy import X" where X is the ultimate class or function name

# flake8: noqa

from ..core.environ import is_module_installed

# ############################################################################
#                                                        Optional KIVY MODULES
# ############################################################################
# "Optional" means that this code is included, but in order to use any of it,
# The optional `kivy` dependencies must be installed, e.g.
#     pip install gypycore[kivy]

if is_module_installed('kivy'):
    from .app_support.dialogs import *
    from .app_support.screens import *
    from .app_support.main_window import *
    from .system_support.kivy_exceptions import *
    from .widgets.background import *
    from .widgets.camera import *
    from .widgets.dropdown import *
    from .widgets.crop_tool import *
    from .widgets.screen_widget import *
    from .widgets.scroll_widget import *
    from .widgets.label import *
    from .widgets.button import *
    from .widgets.hotkey import *
    # from .kivy.assets.fonts import *
    # from .kivy.assets.icons import *
    # from .kivy.assets.images import *
    # from .kivy.assets.key_map import *
    # from .kivy.assets.skins import *
    # from .kivy.assets.svg import *
    # from .kivy.assets.syntax import *

