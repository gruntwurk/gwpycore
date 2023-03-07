from collections import namedtuple
from enum import Enum
from typing import Dict, ClassVar

from gwpycore.core.enums import enum_by_name, enum_default_value

IMMUTABLE = True
MUTABLE = False

__all__ = [
    'IMMUTABLE',
    'MUTABLE',
    'FieldDefs',
    'FieldDescriptor',
]


FieldDescriptor = namedtuple("FieldDescriptor", "type, column_header, immutable", defaults=[MUTABLE])


class FieldDefs():
    def __init__(self, field_defs: Dict[str, FieldDescriptor]) -> None:
        self._field_defs = field_defs

    def initialize_object(self, obj):
        for field_name in self._field_defs:
            value = None
            desc: FieldDescriptor = self._field_defs[field_name]
            if desc.type is str:
                value = ""
            elif issubclass(desc.type, Enum):
                value = enum_default_value(desc.type)
            setattr(obj, field_name, value)

    def from_dict(self, target, source: Dict):
        result = 0
        for field_name in self._field_defs:
            column_header = self._column_header(field_name)
            if column_header in source:
                setattr(target, field_name, self.value_of(field_name, source[column_header]))
                result += 1
        return result

    def as_dict(self,source) -> Dict:
        result = {}
        for field_name in self._field_defs:
            if hasattr(source, field_name):
                column_header = self._column_header(field_name)
                result[column_header] = self.str_of(getattr(source, field_name))
        return result

    def transfer_data(self, target, source, target_subattr='', source_subattr='') -> int:
        """
        Updates the data fields in the `target` object, with the values of the
        corresponding data field in the `source` object -- according to the `field_defs`
        dictionary.

        :param target: The object to receive the data.
        :param source: The object or dictionary that supplies the data.
        :param target_subattr: A child attribute to use with the target object's
            field attribute to actually receive the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.
        :param source_subattr: A child attribute to use with the source object's
            field attribute to actually supply the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.

        :return: The number of fields changed.
        """
        return sum(
            int(self._update_field(
                target, source, field_name,
                target_subattr=target_subattr,
                source_subattr=source_subattr)
                )
            for field_name in self._field_defs
        )

    def column_headers(self) -> list:
        return [self._field_defs[field_name].column_header for field_name in self._field_defs.keys()]

    def types_by_column_name(self) -> dict:
        return {v.column_header: v.type for v in self._field_defs.values()}

    def str_of(self, datum) -> str:
        return datum.name if isinstance(datum, Enum) else str(datum)

    def value_of(self, typ, value_str) -> str:
        try:
            if issubclass(typ, str):
                return value_str
            if issubclass(typ, Enum):
                return enum_by_name(typ, value_str)
            return typ(value_str)
        except Exception:
            return None

    def _field_type(self, field_name):
        if field_name not in self._field_defs:
            return None
        return self._field_defs[field_name].type

    def _column_header(self, field_name):
        if field_name not in self._field_defs:
            return None
        return self._field_defs[field_name].column_header

    def _is_immutable(self, field_name):
        if field_name not in self._field_defs:
            return False
        return bool(self.field_defs[field_name].immutable)

    def _update_field(self, target, source, field_name, target_subattr='', source_subattr='') -> bool:
        """
        Changes the value of the named field (target class attribute) to the
        corresponding attribute from the `source` object -- unless `immutable`
        is `True` and the field (in `target`) already has a value.

        :param target: The object to receive the data.
        :param source: The object that supplies the data.
        :param field_name: Name of the attribute to copy.
        :param immutable: Whether or not to protect an existing value in the target.
            Defaults to False.
        :param target_subattr: A child attribute to use with the target object's
            field attribute to actually receive the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.
        :param source_subattr: A child attribute to use with the source object's
            field attribute to actually supply the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.
        :return: `True` if a change was made; otherwise, `False`.
        """
        if not (hasattr(source, field_name) and hasattr(target, field_name)):
            return False

        typ = self._field_type(field_name)
        immutable = self._is_immutable(field_name)

        current_value = getattr(target, field_name)
        if target_subattr:
            current_value = getattr(current_value, target_subattr)
        if immutable and current_value:
            return False

        new_value = getattr(source, field_name)
        if source_subattr:
            new_value = getattr(source, new_value)
        # if type(current_value) != type(new_value):
        current_value_compare = self.str_of(current_value)
        new_value_compare = self.str_of(new_value)

        if current_value_compare == new_value_compare:
            return False

        if isinstance(current_value, str):
            new_value = new_value_compare
        else:
            new_value = self.value_of(typ, new_value)

        if target_subattr:
            setattr(getattr(target, field_name), target_subattr, new_value)
        else:
            setattr(target, field_name, new_value)
        return True
