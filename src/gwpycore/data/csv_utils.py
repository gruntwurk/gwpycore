import re


__all__ = [
    "csv_header_fixup",
]


def csv_header_fixup(reader):
    # For some strange reason, the first field name contains garbage characters
    first_field_name = reader.fieldnames[0]
    if '"' in first_field_name:
        first_field_name = re.search(r'"([^"]+)"', first_field_name).group(1)
        reader.fieldnames[0] = first_field_name


