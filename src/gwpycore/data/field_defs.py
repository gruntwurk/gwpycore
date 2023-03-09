from collections import namedtuple
from enum import Enum
from typing import Dict

from gwpycore.core.enums import enum_by_name, enum_default_value

__all__ = [
    'IMMUTABLE',
    'MUTABLE',
    'FieldDefs',
    'FieldDescriptor',
]

IMMUTABLE = True
MUTABLE = False


FieldDescriptor = namedtuple("FieldDescriptor", "type, column_header, immutable", defaults=[MUTABLE])


class FieldDefs():
    """
    Generic management of a list of field objects.
    """
    def __init__(self, field_defs: Dict[str, FieldDescriptor]) -> None:
        self._field_defs = field_defs

    def initialize_object(self, target):
        """
        Initializes `obj` with default values for every field (attribute) described herein.
        An attribue is created if it does not already exist.

        :param target: A model object instance to be initialized.
        """
        for field_name in self._field_defs.keys():
            value = None
            desc: FieldDescriptor = self._field_defs[field_name]
            if desc.type is str:
                value = ""
            elif issubclass(desc.type, Enum):
                value = enum_default_value(desc.type)
            setattr(target, field_name, value)

    def from_dict(self, target, source: Dict) -> int:
        """
        Transfers data from a dictionary that is keyed by column headers (not
        the field name) to the target object. Only the dictionary entries that
        correspond to a column header decribed herein are consulted.
        The column headers must match exactly (by casing and punctuation).

        :param target: A model object instance to be initialized.
        :param source: The dictionary with the values to be transferred.
        :return: The mumber of values transferred (even if the traget attribute was already set to that value).
        """
        result = 0
        for field_name in self._field_defs.keys():
            column_header = self._field_defs[field_name].column_header
            if column_header in source:
                result += int(self._update_field(target, field_name, source[column_header]))
        return result

    def as_dict(self, source) -> Dict:
        return {
            self._field_defs[field_name].column_header: self.str_of(getattr(source, field_name))
            for field_name in self._field_defs.keys()
            if hasattr(source, field_name)
        }

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
        result = 0
        for field_name in self._field_defs.keys():
            try:
                source_value = self._source_value(source, field_name, source_subattr=source_subattr)
            except IndexError:
                continue
            result += int(self._update_field(target, field_name, source_value, target_subattr=target_subattr))
        return result

    def column_headers(self) -> list:
        return [self._field_defs[field_name].column_header for field_name in self._field_defs.keys()]

    def types_by_column_name(self) -> dict:
        return {v.column_header: v.type for v in self._field_defs.values()}

    def str_of(self, datum) -> str:
        """
        Converts the given data value to a `str` (with special handling for `Enum` types).
        """
        return datum.name if isinstance(datum, Enum) else str(datum)

    def value_of(self, typ, value_str) -> str:
        """
        Converts the given value string to match the specified class type.
        """
        try:
            if issubclass(typ, str):
                return value_str
            if issubclass(typ, Enum):
                return enum_by_name(typ, value_str)
            return typ(value_str)
        except Exception:
            return None

    def _source_value(self, source, field_name, source_subattr=''):
        """
        :param source: The object that supplies the data.
        :param field_name: Name of the attribute with the value to grab.
        :param source_subattr: A child attribute to use with the source object's
            field attribute to actually supply the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.
        :return: The value supplied.
        """
        if not hasattr(source, field_name):
            raise IndexError(f"Source object {source.__class__.__name__} has no field named '{field_name}'")

        source_value = getattr(source, field_name)
        if source_subattr:
            source_value = getattr(source_value, source_subattr)
        return source_value

    def _update_field(self, target, field_name, new_value, target_subattr='') -> bool:
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
        if not hasattr(target, field_name):
            return False

        current_value = getattr(target, field_name)
        if target_subattr:
            current_value = getattr(current_value, target_subattr)
        if self._field_defs[field_name].immutable and current_value:
            return False

        new_value_compare = self.str_of(new_value)

        if self.str_of(current_value) == new_value_compare:
            return False

        if isinstance(current_value, str):
            new_value = new_value_compare
        else:
            new_value = self.value_of(self._field_defs[field_name].type, new_value)

        if target_subattr:
            setattr(getattr(target, field_name), target_subattr, new_value)
        else:
            setattr(target, field_name, new_value)
        return True