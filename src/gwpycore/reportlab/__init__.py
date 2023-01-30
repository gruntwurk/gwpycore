# The existence of this file makes this subfolder a "package"

# The following imports make it so that the client only has to say
# "from gwpycore.kivy import X" where X is the ultimate class or function name

# flake8: noqa

from ..core.environ import is_module_installed

# ############################################################################
#                                                   Optional REPORTLAB MODULES
# ############################################################################
# "Optional" means that this code is included, but in order to use any of it,
# The optional `reportlab` dependencies must be installed, e.g.
#     pip install gypycore[reportlab]

if is_module_installed('reportlab'):
    from .rl_fonts import *
    from .flowables.text_flowables import *
    from .templates.multi_column import *
    from .templates.id_badge import *

