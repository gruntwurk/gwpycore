from collections import Iterable
from pathlib import Path
from typing import Dict, Optional, Union
from gwpycore.gw_basis.gw_config import GWConfigParser, ThemeMetaData, find_themes
import logging

LOG = logging.getLogger("main")


class SyntaxHighlightSpecs:
    """
    If you pass in an existing color map, then the colors loaded form
    the syntax file will be restricted to the keywords named.
    Otherwise, all of the keywords in the file will be assumed valid.
    color_map = {
        "background": (0,0,0),
        "text": (0,0,0),
        "link": (0,0,0),
        "headertext": (0,0,0),
        ...
        }
    syntax_specs = SyntaxHighlightSpecs("C:/app/assets/themes", color_map, "sunrise", parent)
    """

    def __init__(
        self,
        root_path: Union[Path, str],
        color_map: Optional[Dict[str, tuple]] = None,
        current_theme_name="",
        parent=None,
    ):
        if isinstance(root_path, Path):
            self.root_path = root_path
        if root_path is str:
            self.root_path = Path(root_path)
        self.color_map = color_map
        self.theme_name = current_theme_name
        self.parent = parent
        self.available_syntax_themes: Dict[str,ThemeMetaData] = []
        self.syntax_meta: ThemeMetaData = None
        self.load_syntax()

    def change_theme(self, theme_name):
        if self.theme_name == theme_name:
            return
        self.theme_name = theme_name
        self.load_syntax()

    def load_syntax(self):
        if not self.theme_name:
            return
        syntax_file = self.root_path / self.theme_name / "syntax.conf"

        parser = GWConfigParser(LOG)
        parser.parse_file(syntax_file)

        section = "Main"
        if parser.has_section(section):
            self.syntax_meta.name = parser[section].gettext("name", "")
            self.syntax_meta.description = parser[section].gettext("description", "")
            self.syntax_meta.author = parser[section].gettext("author", "")
            self.syntax_meta.credit = parser[section].gettext("credit", "")
            self.syntax_meta.url = parser[section].gettext("url", "")
            self.syntax_meta.license = parser[section].gettext("license", "")
            self.syntax_meta.license_url = parser[section].gettext("licenseurl", "")

        section = "Syntax"
        if parser.has_section(section):
            for option in parser.items(section):
                if option not in self.color_map:
                    LOG.warning(
                        f"Syntax theme {self.theme_name} refers to a syntax element '{option}' that doesn't exist."
                    )
                else:
                    self.color_map[option] = parser[section].getcolor(option)
        LOG.info("Loaded syntax theme '%s'" % self.theme_name)

    def syntax_list(self):
        """Scan the syntax themes folder and list all themes."""
        if self.available_syntax_themes:
            return self.available_syntax_themes
        self.available_syntax_themes = find_themes(self.root_path,"syntax.conf")
        if self.theme_name not in self.available_syntax_themes:
            self.theme_name = ""
        return self.available_syntax_themes
