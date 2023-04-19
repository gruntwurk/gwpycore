from collections import namedtuple
from enum import Enum
from typing import Dict

from gwpycore.core.enums import enum_by_name, enum_by_value, enum_default_value

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
            elif desc.type is int:
                value = 0
            elif desc.type is float:
                value = 0.0
            elif desc.type is bool:
                value = False
            elif issubclass(desc.type, Enum):
                value = enum_default_value(desc.type)
            setattr(target, field_name, value)

    def from_dict(self, target, source: Dict, force=False) -> int:
        """
        Transfers data from a dictionary that is keyed by column headers (not
        the field name) to the target object. Only the dictionary entries that
        correspond to a column header decribed herein are consulted.
        The column headers must match exactly (by casing and punctuation).

        :param target: A model object instance to be initialized or updated.
        :param source: The dictionary with the values to be transferred.
        :param force: Whether or not to override a field's immutability.
            Defaults to `False`.

        :return: The mumber of values in the target that were changed.
        """
        return sum(
            int(self._update_field(target, field_name, source[field_def.column_header], force=force))
            for field_name, field_def in self._field_defs.items()
            if field_def.column_header in source
        )

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
        for field_name in self._field_defs:
            try:
                source_value = self._source_value(source, field_name, source_subattr=source_subattr)
            except IndexError:
                continue
            result += int(self._update_field(target, field_name, source_value, target_subattr=target_subattr))
        return result

    def column_headers(self) -> list:
        return [field_def.column_header for field_def in self._field_defs.values()]

    def types_by_column_name(self) -> dict:
        return {v.column_header: v.type for v in self._field_defs.values()}

    def str_of(self, datum) -> str:
        """
        Converts the given data value to a `str` (with special handling for `Enum` types).
        """
        return datum.display_name() if hasattr(datum, 'display_name') else str(datum)

    def value_of(self, typ, value_str):
        """
        Converts the given value string to match the specified class type.
        """
        try:
            if issubclass(typ, str):
                return value_str
            if issubclass(typ, Enum):
                return enum_by_value(typ, value_str)
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
            if not source_value:
                return None
            source_value = getattr(source_value, source_subattr)
        return source_value

    def _update_field(self, target, field_name, new_value, target_subattr='', force=False) -> bool:
        """
        Changes the value of the named field (target class attribute) to the
        corresponding attribute from the `source` object -- unless `immutable`
        is `True` and the field (in `target`) already has a value.

        :param target: The object to receive the data.
        :param field_name: Name of the attribute to copy.
        :param new_value: The datum.
        :param target_subattr: A child attribute to use with the target object's
            field attribute to actually receive the data. For example, the
            attributes of a Kivy widget object will all refer to child widgets,
            which in turn have a `text` property that actually holds the data.
        :param force: Whether or not to override the field's immutability.
            Defaults to `False`.

        :return: `True` if a change was made; otherwise, `False`.
        """
        if not hasattr(target, field_name):
            setattr(target, field_name, None)

        field_def = self._field_defs[field_name]
        current_value = getattr(target, field_name)
        if current_value and target_subattr:
            current_value = getattr(current_value, target_subattr)
        if not force and field_def.immutable and current_value:
            return False

        new_value_compare = self.str_of(new_value)
        if self.str_of(current_value) == new_value_compare:
            return False

        if isinstance(current_value, str):
            new_value = new_value_compare
        elif not isinstance(new_value, field_def.type):
            new_value = self.value_of(field_def.type, new_value)

        if target is None:
            return False

        if target_subattr:
            target_object = getattr(target, field_name)
            if target_object is None:
                return False
            setattr(target_object, target_subattr, new_value)
        else:
            setattr(target, field_name, new_value)
        return True
