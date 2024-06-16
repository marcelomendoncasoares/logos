"""
SQLite Document Store for llama-index.

"""

from pathlib import Path
from typing import Any, Self

from llama_index.storage.docstore.keyval_docstore import KVDocumentStore
from llama_index.storage.docstore.types import DEFAULT_BATCH_SIZE
from llama_index.storage.index_store.keyval_index_store import KVIndexStore
from llama_index.storage.kvstore.postgres_kvstore import PostgresKVStore, get_data_model
from pydantic import BaseModel


def _pydantic_to_dict(obj: Any) -> Any:
    """
    Recursively convert Pydantic models to dictionaries for JSON serialization.
    """
    if isinstance(obj, BaseModel):
        obj = obj.model_dump()
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(_pydantic_to_dict(v) for v in obj)
    if isinstance(obj, dict):
        return {k: _pydantic_to_dict(v) for k, v in obj.items()}
    return obj


class SQLiteKVStore(PostgresKVStore):
    """
    SQLite key-value store.
    """

    def __init__(  # noqa: PLR0913
        self,
        database_path: str | Path,
        table_name: str = "kvstore",
        *,
        perform_setup: bool = True,
        debug: bool = False,
        use_jsonb: bool = False,
    ) -> None:
        """
        Initialize a SQLiteKVStore.

        Args:
            database_path: Path to the SQLite database file.
            table_name: Name of the table.
            perform_setup: Whether to perform setup on initialization.
            debug: Whether to enable debug mode.
            use_jsonb: Whether to use JSONB data type.
        """
        self.connection_string = f"sqlite:///{database_path}"
        self.async_connection_string = f"sqlite+aiosqlite:///{database_path}"
        self.table_name = table_name.lower()
        self.schema_name = "main"
        self.perform_setup = perform_setup
        self.debug = debug
        self.use_jsonb = use_jsonb
        self._is_initialized = False

        from sqlalchemy.orm import declarative_base

        self._base = declarative_base()
        self._table_class = get_data_model(
            base=self._base,
            index_name=self.table_name,
            schema_name=self.schema_name,
            use_jsonb=self.use_jsonb,
        )

    def _create_schema_if_not_exists(self) -> None:
        """
        SQLite does not have schemas, so this method does nothing.
        """
        return

    def put_all(self, kv_pairs: list[tuple[str, dict]], *args, **kwargs) -> None:
        """
        Put all key-value pairs, parsing Pydantic models to dictionaries.
        """
        kv_pairs = [(k, _pydantic_to_dict(v)) for k, v in kv_pairs]
        super().put_all(kv_pairs, *args, **kwargs)

    async def aput_all(self, kv_pairs: list[tuple[str, dict]], *args, **kwargs) -> None:
        """
        Put all key-value pairs asynchronously, parsing Pydantic models to dictionaries.
        """
        kv_pairs = [(k, _pydantic_to_dict(v)) for k, v in kv_pairs]
        super().put_all(kv_pairs, *args, **kwargs)


class SQLiteDocumentStore(KVDocumentStore):
    """
    SQLite Document Store for Document and Node objects.
    """

    def __init__(
        self,
        kvstore: SQLiteKVStore,
        namespace: str | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Initialize a SQLiteDocumentStore.

        Args:
            kvstore: SQLiteKVStore instance.
            namespace: Namespace for the docstore.
            batch_size: Batch size for bulk operations.
        """
        super().__init__(kvstore, namespace, batch_size)

    @classmethod
    def from_database_path(
        cls,
        database_path: str | Path,
        table_name: str = "docstore",
        namespace: str | None = None,
    ) -> Self:
        """Load a SQLiteDocumentStore from a SQLite database path."""
        kvstore = SQLiteKVStore(
            database_path=database_path,
            table_name=table_name,
        )
        return cls(kvstore, namespace)


class SQLiteIndexStore(KVIndexStore):
    """
    SQLite Index Store.
    """

    def __init__(
        self,
        kvstore: SQLiteKVStore,
        namespace: str | None = None,
    ) -> None:
        """
        Initialize a SQLiteIndexStore.

        Args:
            kvstore: SQLiteKVStore instance.
            namespace: Namespace for the docstore.
        """
        super().__init__(kvstore, namespace)

    @classmethod
    def from_database_path(
        cls,
        database_path: str | Path,
        table_name: str = "indexstore",
        namespace: str | None = None,
    ) -> Self:
        """Load a SQLiteIndexStore from a SQLite database path."""
        kvstore = SQLiteKVStore(
            database_path=database_path,
            table_name=table_name,
        )
        return cls(kvstore, namespace)
