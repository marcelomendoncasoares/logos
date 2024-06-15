"""
Quick implementation just to prove the concept.

This is a simple in-memory key-value store that can be persisted to disk using pickle.

"""

import pickle

from pathlib import Path

import fsspec

from llama_index.storage.kvstore.simple_kvstore import SimpleKVStore


class SimplePickleKVStore(SimpleKVStore):
    """
    Simple in-memory Key-Value store that can be persisted to disk using pickle.

    """

    def persist(
        self,
        persist_path: str,
        fs: fsspec.AbstractFileSystem | None = None,
    ) -> None:
        """Persist the store."""
        fs = fs or fsspec.filesystem("file")
        dirpath = str(Path(persist_path).parent)
        if not fs.exists(dirpath):
            fs.makedirs(dirpath, exist_ok=True)
        with fs.open(persist_path, "w") as f:
            f.write(str(pickle.dumps(self._data)))

    @classmethod
    def from_persist_path(
        cls,
        persist_path: str,
        fs: fsspec.AbstractFileSystem | None = None,
    ) -> "SimpleKVStore":
        """Load a SimpleKVStore from a persist path and filesystem."""
        fs = fs or fsspec.filesystem("file")
        with fs.open(persist_path, "rb") as f:
            data = pickle.loads(bytes(f.read()))  # noqa: S301
        return cls(data)
