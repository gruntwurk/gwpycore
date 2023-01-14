import os
import sys
import webbrowser
from urllib.request import pathname2url

webbrowser.open(f"file://{pathname2url(os.path.abspath(sys.argv[1]))}")
