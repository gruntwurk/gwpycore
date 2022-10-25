import csv
from datetime import datetime
from enum import Enum
import re
from csv import DictReader

from pathlib import Path
from typing import Dict, List, Tuple, Union

from ..core.gw_datetime import as_datetime
from ..core.gw_exceptions import GWValueInterpretationWarning
from ..core.booleans import as_bool
from ..core.gw_numeric import as_int, as_float
from ..core.gw_colors import NamedColor, as_color, as_named_color
from ..core.gw_files import as_path


__all__ = [
    "csv_header_fixup",
    "interpret_values",
    "import_csv_file",
]


def csv_header_fixup(reader: DictReader):
    """For some strange reason, the first field name contains garbage characters"""
    first_field_name = reader.fieldnames[0]
    if '"' in first_field_name:
        first_field_name = re.search(r'"([^"]+)"', first_field_name).group(1)
        reader.fieldnames[0] = first_field_name


def import_csv_file(csv_file: Union[Path, str], field_types: Dict) -> Tuple:
    rows = []
    with Path(csv_file).open('rt') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_header_fixup(reader)
        # print(reader.fieldnames)

        accumulated_warnings = []
        row_no = 0
        for row in reader:
            row_no += 1
            warnings = interpret_values(row, field_types, context=f"row {row_no}")
            accumulated_warnings.extend(warnings)
            rows.append(row)
    return rows, accumulated_warnings


def interpret_values(row: Dict, field_types: Dict, context: str = None) -> List[GWValueInterpretationWarning]:
    """
    Converts the values within a Dict (e.g. the Dict returned by csv.DictReader
    for each row) from strings to other types, according to the `field_types`
    dictionary.
    NOTE: The matching of field names is case-sensitive.

    :param row: A dictionary (with all string values) -- updated in place.

    :param field_types: A dictionary that maps field names to types. For example,
    `{"name": str, "id": int, "status_color": NamedColor, "attachments": pathlib.Path}`.
    The value can by a Python primitive type (str, int), a class type (pathlib.Path),
    or a string naming the type ("str", "int", "path"), as follows:

        int or "int" -- calls int()
        float or "float" -- calls float()
        bool or "bool" -- calls as_bool()
        pathlib.Path or "path" -- calls as_path()
        gypycore.NamedColor or "namedcolor" -- calls as_named_color()
        "color" -- calls as_color (returns a Tuple[int])
        any subclass of Enum -- returns the enum value that corresponds to the data string value (by name)
        str or "str" (or anything else) -- no change

    :param context: (optional) a string that describes the source of the data
    (e.g. a row number), in the event that a warning needs to be reported.

    :return: A list of GWValueInterpretationWarning for any field conversions that failed.
    """
    warnings = []
    for key, value in row.items():
        if key in field_types:
            typ = field_types[key]
            if type(typ) is str:
                typ = typ.casefold()
            try:
                if typ is int or typ == 'int':
                    row[key] = as_int(value)
                elif typ is float or typ == 'float':
                    row[key] = as_float(value)
                elif typ is bool or typ == 'bool':
                    row[key] = as_bool(value)
                elif typ is datetime or typ in ['datetime', 'date', 'time']:
                    row[key] = as_datetime(value)
                elif typ is Path or typ == 'path':
                    row[key] = as_path(value)
                elif type == 'color':
                    row[key] = as_color(value)
                elif typ is NamedColor or type == 'namedcolor':
                    row[key] = as_named_color(value)
                elif issubclass(typ, Enum):
                    row[key] = typ[value]
            except Exception:
                warnings.append(GWValueInterpretationWarning(key, value, context=context, possible_values=str(typ)))
    return warnings


