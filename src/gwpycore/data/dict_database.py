from abc import ABC, abstractmethod
import csv
import logging
from pathlib import Path
from typing import Callable, Dict, List, Union

from ..core.exceptions import GWIndexError
from ..core.files import save_backup_file
from ..data.csv_utils import csv_header_fixup


LOG = logging.getLogger("gwpy")


class MemoryEntry(ABC):
    """
    Abstract base class for a simple database entry.
    """
    _key = None
    _hidden = False

    @property
    def key(self):
        """How the entry is indexed in the database."""
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def hidden(self):
        """The hidden property, i.e. whether or not the entry has been 'soft deleted'."""
        return self._hidden

    @hidden.setter
    def hidden(self, value):
        self._hidden = value

    @abstractmethod
    def index_key(self) -> str:
        """
        Override this method to customize how entry is indexed (e.g. according
        to a combintion of some other fields).
        """
        return self._key

    @abstractmethod
    def display_text(self) -> str:
        """
        Override this method to provide a human-readable summary of the entry).
        """
        return self.__repr__()

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
        if alt_key in self.db:
            return self.db[alt_key]
        return None

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

    def new_entry(self, key: str = "__new__") -> MemoryEntry:
        """
        Creates a new entry and adds it to the database.

        :return: The new entry (unless there is already an entry by the
        given key, in which case that instance is returned).
        """
        if key in self.db:
            return self.db[key]
        entry = self._content_class()
        entry.key = key
        self.db[entry.key] = entry
        return entry

    def rekey(self, entry: MemoryEntry):
        """
        Re-indexes the entry within the database according to the entry's
        index_key() function.

        :param entry: The entry to be rekeyed.

        :return: True if successful; otherise, False if index_key() is empty
        and thus, there's nothing to rekey it to.

        :raises GWIndexError:
        """
        if not entry.index_key():
            raise GWIndexError(f"Cannot rekey an entry when index_key() returns an empty value.")
        if entry._key and entry._key not in self.db:
            # this shouldn't happen, but just in case...
            self.new_entry(entry)
            return True
        if entry.index_key() != entry._key:
            if entry._key:
                self.db.pop(entry._key)
            entry._key = entry.index_key()
            self.db[entry._key] = entry

    def dump(self) -> List[str]:
        lines = []
        for k in self.db:
            lines.append(f"{k}: {self.db[k].display_text()}")
        return lines

    def load(self):
        with self._persistence_filepath.open('rt') as csvfile:
            reader = csv.DictReader(csvfile, restval='')
            csv_header_fixup(reader)

            for row in reader:
                entry = self.new_entry("__loading__")
                try:
                    entry.from_dict(row)
                    self.rekey(entry)
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
        for entry in self.db.values():
            if include_hidden or not entry._hidden:
                text_data.append(entry.as_text_record())
        self._persistence_filepath.write_text("\n".join(text_data))
        LOG.trace("DB saved.")


__all__ = [
    "MemoryEntry",
    "MemoryDatabase",
]