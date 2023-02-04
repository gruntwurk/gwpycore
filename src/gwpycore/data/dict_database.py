from abc import ABC, abstractmethod
import csv
import logging
from pathlib import Path
from typing import Callable, Dict, List, Union

from ..core.exceptions import GWException
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
    TODO describe _entry_id and _description fields
    """
    def __init__(self) -> None:
        super().__init__()
        self._entry_id = ""
        self_description = ""
        self._hidden = False
        self._is_new = False

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

    @abstractmethod
    def index_key(self) -> str:
        """
        Override this method to customize how entry is indexed (e.g. according
        to a combination of some other fields).

        When store is called, this is what it'll (re)key it as.
        """
        return self._entry_id

    @abstractmethod
    def temp_key(self) -> str:
        """
        Override this method to customize how the entry is indexed -- on a
        temporary basis -- (e.g. according to a combination of some other fields).

        When store is called, this is what it'll rekey _from_.
        """
        return self._description

    @abstractmethod
    def from_text_record(self, line: str):
        """
        Override this method to parse the entry from a line of text (e.g. CSV).
        """
        pass

    @abstractmethod
    def from_dict(self, data: Dict):
        """
        Override this method to load an entry from a Dict that is keyed on field names.
        """
        pass

    @classmethod
    def header_record(cls) -> str:
        """
        Override this method to return any header line to be written at the
        start of the file. May contain newlines.
        """
        return ""

    @abstractmethod
    def as_text_record(self) -> str:
        """
        Override this method to convert the entry to a single line of text (e.g.
        as CSV or fixed fields), suitable for persisting to a text file.
        """
        return self.__repr__()


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

    def integrity_errors(self) -> List[str]:
        errors = []
        for k in self.db:
            v = self.db[k]
            if not v :
                errors.append(f"Database entry '{k}' has a null value.")
            elif k != v.index_key():
                errors.append(f"Database entry '{k}' does not match its value's.index_key() of '{v.index_key()}' ")
        return errors

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
        if errs := self.integrity_errors():
            raise GWException("\n".join(errs))
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
