"""File-backed LRU cache implemented with a hash map and linked list."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from doubly_linked_list import DoublyLinkedList, Node


@dataclass(frozen=True)
class CachedFile:
    """Public information about a file currently held in the cache."""

    path: Path
    size_bytes: int


class FileNotCachedError(LookupError):
    """Raised when a cache-only read is requested for a file not in cache."""


class FileCache:
    """Cache text files using O(1) hash-map and doubly-linked-list operations.

    The linked list is ordered from least recently used (first) to most
    recently used (last). Cache statistics are cumulative and are not reset by
    :meth:`clear`.
    """

    def __init__(self, capacity: int = 3) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            raise ValueError("Cache capacity must be a positive integer.")

        self.capacity = capacity
        self._entries: Dict[str, Node] = {}
        self._recency = DoublyLinkedList()
        self.cache_hits = 0
        self.cache_misses = 0
        self.evicted_files_count = 0

    @staticmethod
    def _normalize_path(file_path: str | Path) -> Path:
        return Path(file_path).expanduser().resolve()

    def open_file(self, file_path: str | Path) -> str:
        """Read a text file, returning cached contents when available.

        A cache miss is recorded even when the path does not exist or cannot be
        decoded. The file is inserted only after a successful read.
        """
        path = self._normalize_path(file_path)
        key = str(path)
        cached_node = self._entries.get(key)

        if cached_node is not None:
            self.cache_hits += 1
            self._recency.move_to_end(cached_node)
            return cached_node.value

        self.cache_misses += 1
        contents = path.read_text(encoding="utf-8")
        self._insert(key, contents)
        return contents

    def read_cached_file(self, file_path: str | Path) -> str:
        """Return a file only if it is already cached, updating its recency."""
        key = str(self._normalize_path(file_path))
        cached_node = self._entries.get(key)
        if cached_node is None:
            self.cache_misses += 1
            raise FileNotCachedError(f"{Path(key).name} is not currently cached.")

        self.cache_hits += 1
        self._recency.move_to_end(cached_node)
        return cached_node.value

    def _insert(self, key: str, contents: str) -> None:
        node = self._recency.append(key, contents)
        self._entries[key] = node

        if len(self._entries) > self.capacity:
            least_recently_used = self._recency.pop_first()
            if least_recently_used is not None:
                del self._entries[least_recently_used.key]
                self.evicted_files_count += 1

    def list_cached_files(self) -> List[CachedFile]:
        """Return cached files in LRU-to-MRU order."""
        result = []
        for node in self._recency:
            path = Path(node.key)
            result.append(
                CachedFile(path=path, size_bytes=len(node.value.encode("utf-8")))
            )
        return result

    def search_cached_files(self, query: str) -> List[CachedFile]:
        """Find cached paths whose filename contains ``query`` (case-insensitive)."""
        normalized_query = query.casefold()
        return [
            cached_file
            for cached_file in self.list_cached_files()
            if normalized_query in cached_file.path.name.casefold()
        ]

    def get_statistics(self) -> dict[str, int]:
        """Return a snapshot of cache counters and current occupancy."""
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "current_cache_size": len(self._entries),
            "capacity": self.capacity,
            "evicted_files_count": self.evicted_files_count,
        }

    def clear(self) -> None:
        """Empty the cache without resetting cumulative statistics."""
        self._entries.clear()
        self._recency.clear()
