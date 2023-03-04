from abc import ABC, abstractmethod
import csv
from enum import Enum
import logging
from pathlib import Path
from typing import Callable, Dict, List, Union

from ..core.exceptions import GWException, GWWarning
from ..core.files import save_backup_file
from ..data.csv_utils import csv_header_fixup

__all__ = [
    "MemoryEntry",
    "MemoryDatabase",
]

LOG = logging.getLogger("gwpy")


# ############################################################################
#                                                                 MEMORY ENTRY
# ############################################################################

class MemoryEntry(ABC):
    """
    Abstract base class for a simple database entry.

    1. Override the static `_field_defs` dictionary to list all of your object member
       names and corresponding data types and column headers e.g.
       {
         '_entry_id': (str, 'Reference'),
         '_description': (str, 'Name'),
         'member_rank': (int, 'Rank'),
         '_issued': (datetime, 'Date Issued'),
        }
    2. The `_entry_id` field is used as the primary index for the entry.
       Define a pair of properties over it (so that you can refer to it
       as `member_id`, for example).
    3. The `_description` field is used, for one thing, as the temporary index
       for the entry, in case `_entry_id` is None. Define a pair of properties
       over it (so that you can refer to it as `full_name`, for example).
    4. Optionally override `index_key()` if you don't want it to just return
       `_entrty_id`
    5. Optionally override `temp_key()` if you don't want it to just return
       `_description.casefold()`
    6. Override `from_dict()` and `as_dict()`
    7. Optionally override `from_text_record()` and `as_text_record()` if you
       don't want them to depend on `from_dict()` and `as_dict()`.
    8. Optionally override `header_record()` (class method) if you don't want
       it just return `_field_defs[`member name`][1]`.
    """

    # Static class fields
    # Dict of: 'object member name': (field type, 'column heading')
    # e.g. {'role': (MemberRole, 'Member Role') }
    _field_defs = {}

    def __init__(self, data=None) -> None:
        super().__init__()
        self._entry_id = ""
        self._description = ""
        self._hidden = False
        self._is_new = False
        self._initialize_field_defs()
        if not data:
            return

        if isinstance(data, dict):
            self.from_dict(data)
        elif isinstance(data, str):
            self.from_text_record(data)
        elif isinstance(data, self.__class__):
            self.assign(data)

    def _initialize_field_defs(self):
        for field_name in self._field_defs:
            typ = self._field_defs[field_name][0]
            # heading = self._field_defs[field_name][1]
            value = "" if typ is str else None
            if isinstance(typ, Enum) and hasattr(typ, 'default_member'):
                value = typ.default_member()
            setattr(self, field_name, value)

    def update_field(self, other, field_name, immutable=False) -> bool:
        """
        Changes the value of the named field (class member) to the
        corresponding value from the `other` object -- unless `immutable`
        is `True` and the field (in `self`) already has a value.

        :param other: The object with the data to import.
        :param field_name: Name of the attribute to copy from `other` to `self`
        :param immutable: Whether or not to protect an existing value.
            Defaults to False
        :return: `True` if a change was made; otherwise, `False`.
        """
        if not hasattr(other, field_name):
            return False
        current_value = getattr(self, field_name)
        if immutable and current_value:
            return False
        new_value = getattr(other, field_name)
        if current_value == new_value:
            return False
        setattr(self, field_name, new_value)
        return True

    @property
    def hidden(self):
        """The hidden property, i.e. whether or not the entry has been 'soft deleted'."""
        return self._hidden

    @hidden.setter
    def hidden(self, value):
        self._hidden = value

    @property
    def is_new(self):
        """The _is_new property."""
        return self._is_new

    @is_new.setter
    def is_new(self, value):
        self._is_new = value

    def index_key(self) -> str:
        """
        Override this method to customize how entry is indexed (e.g. according
        to a combination of some other fields).

        When `store()` is called, this is what it'll (re)key it as.
        """
        return self._entry_id

    def temp_key(self) -> str:
        """
        Override this method to customize how the entry is indexed -- on a
        temporary basis -- (e.g. according to a combination of some other fields).

        When `store()` is called, this is what it'll rekey _from_.
        """
        return self._description.casefold()

    def from_text_record(self, line: str):
        """
        Override this method to parse the entry from a line of text (e.g. CSV).
        """
        # Padding with extra commas ensures that there are more data values than column headers
        data_values_list = (line + "," * len(self._field_defs.keys())).split(",")
        self.from_dict(dict(zip(self.column_names(), data_values_list)))

    @abstractmethod
    def from_dict(self, data: Dict):
        """
        Override this method to load an entry from a Dict that is keyed on field names.
        """
        pass

    def as_dict(self) -> Dict:
        """
        Returns a dict of this object's data that is keyed on column headings, as per
        `self._field_defs`. Override it if necessary.
        """
        result = {}
        for k, v in self._field_defs:
            typ = v[0]
            data_value = getattr(self, k)
            if typ is str and data_value is None:
                data_value = ''
            if isinstance(typ, Enum):
                data_value = data_value.name
            result[v[1]] = data_value
        return result

    @classmethod
    def header_record(cls) -> str:
        """
        Override this method to return any header line to be written at the
        start of the file. May contain newlines.
        """
        return ','.join(cls.column_names())

    @classmethod
    def column_names(cls) -> list:
        return [cls._field_defs[key][1] for key in cls._field_defs.keys()]

    @classmethod
    def types_by_column_name(cls) -> dict:
        return {v[1]: v[0] for v in cls._field_defs.values()}

    def as_text_record(self) -> str:
        """
        Returns the entry as a single line of text, suitable for persisting to
        a text file. The default implementation is a simple CSV string.
        Override this method if desired.
        """
        # FIXME change this to a CSV writer
        return ",".join([f'"{v}"' for v in self.as_dict().values()])



# ############################################################################
#                                                              MEMORY DATABASE
# ############################################################################

class MemoryDatabase(ABC):
    """
    Abstract base class for an in-memory database that is loaded from disk when
    the app needs it and is then written back to disk when the app is done
    using it.

    :param content_class: The class of the object to be contained in the
    database. Must be a subclass of `MemoryEntry`.

    :param persistence_filepath: Fully qualified path of the file that contains
    (is to contain) the persisted data.

    :param backup_folder: If specified, a copy of the origiinal file will be wriiten
    to here (with a timestamp added to the name). Default is None.
    """
    def __init__(self, content_class, persistence_filepath: Union[str, Path], backup_folder: str = None):
        self._content_class = content_class
        self.db = {}
        filepath = Path(persistence_filepath)
        self._persistence_filepath = filepath
        self._persistence_folder = filepath.parent
        self._persistence_file_basename = filepath.stem
        self._persistence_file_ext = filepath.suffix
        self._backup_folder = Path(backup_folder) if backup_folder else None
        self._using_header = bool(self._content_class.header_record())

    def get(self, key: str, alt_key: str = ''):
        if key in self.db:
            return self.db[key]
        return self.db[alt_key] if alt_key in self.db else None

    def values(self):
        return self.db.values()

    def sorted_values(self, sort_value_fn: Callable):
        sort_order = []
        for entry in self.values():
            key = sort_value_fn(entry)
            sort_order.append((key, entry.index_key()))
        return [self.get(index) for _, index in sorted(sort_order)]

    def len(self):
        """Number of entries in the DB."""
        return len(self.db)

    def new_entry(self) -> MemoryEntry:
        """
        Creates a new entry and adds it to the database.

        :return: The new entry.
        """
        entry = self._content_class()
        entry.is_new = True
        return entry

    def store(self, entry):
        """
        Stores the entry in the database, rekeying the entry from the temp_key to the index_key if necessary.
        """
        if not entry.index_key():
            return
        if entry.index_key() != entry.temp_key():
            self.db.pop(entry.temp_key(), None)
        self.db[entry.index_key()] = entry
        entry.is_new = False

    def dump(self) -> List[str]:
        return [f"{k}: {str(self.db[k])}" for k in self.db]

    def load(self):
        with self._persistence_filepath.open('rt') as csvfile:
            reader = csv.DictReader(csvfile, restval='')
            csv_header_fixup(reader)

            for row in reader:
                entry = self.new_entry()
                try:
                    entry.from_dict(row)
                    self.store(entry)
                except Exception as e:
                    LOG.warning(f'Error while parsing: {row}')
                    LOG.exception(e)

    def save(self, include_hidden=True):
        """
        This default implementation writes the data to a simple text file with
        one line per record (in whatever format is returned by
        entry.as_text_record().)

        Override this method if something more complicated than one line per
        record is needed.

        :param include_hidden: Whether or not to include entries that are
        marked with the _hidden flag. Default is True.
        """
        # TODO A: Change this to a csv.writer and then remove as_text_record()
        LOG.trace("Saving DB")
        if self._backup_folder:
            save_backup_file(self._persistence_filepath, self._backup_folder)
        text_data = []
        if self._using_header:
            text_data.append(self._content_class.header_record())
        entry: MemoryEntry
        text_data.extend(
            entry.as_text_record()
            for entry in self.db.values()
            if include_hidden or not entry._hidden
        )
        self._persistence_filepath.write_text("\n".join(text_data))
        LOG.trace("DB saved.")
