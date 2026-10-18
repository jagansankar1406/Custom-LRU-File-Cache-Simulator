"""Unit tests for the file cache and its LRU behavior."""

import tempfile
import unittest
from pathlib import Path

from doubly_linked_list import DoublyLinkedList
from file_cache import FileCache, FileNotCachedError
from main import SAMPLE_FILES, create_sample_files


class DoublyLinkedListTests(unittest.TestCase):
    def test_append_move_and_pop_preserve_order(self) -> None:
        linked_list = DoublyLinkedList()
        first = linked_list.append("first", "1")
        linked_list.append("second", "2")
        linked_list.append("third", "3")

        linked_list.move_to_end(first)
        self.assertEqual([node.key for node in linked_list], ["second", "third", "first"])
        self.assertEqual(linked_list.pop_first().key, "second")
        self.assertEqual([node.key for node in linked_list], ["third", "first"])

    def test_clear_resets_list(self) -> None:
        linked_list = DoublyLinkedList()
        linked_list.append("one", "1")
        linked_list.clear()
        self.assertEqual(len(linked_list), 0)
        self.assertIsNone(linked_list.head)
        self.assertIsNone(linked_list.tail)


class FileCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.paths = []
        for name in ("alpha.txt", "bravo.txt", "charlie.txt", "delta.txt"):
            path = self.directory / name
            path.write_text(f"contents of {name}", encoding="utf-8")
            self.paths.append(path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_open_file_records_miss_then_hit(self) -> None:
        cache = FileCache(capacity=2)
        self.assertEqual(cache.open_file(self.paths[0]), "contents of alpha.txt")
        self.assertEqual(cache.open_file(self.paths[0]), "contents of alpha.txt")
        stats = cache.get_statistics()
        self.assertEqual(stats["cache_misses"], 1)
        self.assertEqual(stats["cache_hits"], 1)
        self.assertEqual(stats["current_cache_size"], 1)

    def test_cache_evicts_least_recently_used_file(self) -> None:
        cache = FileCache(capacity=3)
        for path in self.paths[:3]:
            cache.open_file(path)

        # Make alpha most recently used, so bravo is now the LRU item.
        cache.open_file(self.paths[0])
        cache.open_file(self.paths[3])

        cached_names = [item.path.name for item in cache.list_cached_files()]
        self.assertEqual(cached_names, ["charlie.txt", "alpha.txt", "delta.txt"])
        self.assertEqual(cache.get_statistics()["evicted_files_count"], 1)
        with self.assertRaises(FileNotCachedError):
            cache.read_cached_file(self.paths[1])

    def test_read_cached_file_updates_lru_order(self) -> None:
        cache = FileCache(capacity=2)
        cache.open_file(self.paths[0])
        cache.open_file(self.paths[1])
        cache.read_cached_file(self.paths[0])
        cache.open_file(self.paths[2])
        self.assertEqual(
            [item.path.name for item in cache.list_cached_files()],
            ["alpha.txt", "charlie.txt"],
        )

    def test_search_is_case_insensitive_and_does_not_change_stats(self) -> None:
        cache = FileCache(capacity=3)
        cache.open_file(self.paths[0])
        before = cache.get_statistics()
        matches = cache.search_cached_files("ALP")
        self.assertEqual([item.path.name for item in matches], ["alpha.txt"])
        self.assertEqual(cache.get_statistics(), before)

    def test_missing_file_counts_as_miss_but_is_not_cached(self) -> None:
        cache = FileCache(capacity=2)
        with self.assertRaises(FileNotFoundError):
            cache.open_file(self.directory / "missing.txt")
        self.assertEqual(cache.get_statistics()["cache_misses"], 1)
        self.assertEqual(cache.get_statistics()["current_cache_size"], 0)

    def test_clear_empties_cache_and_preserves_counters(self) -> None:
        cache = FileCache(capacity=2)
        cache.open_file(self.paths[0])
        cache.open_file(self.paths[0])
        cache.clear()
        stats = cache.get_statistics()
        self.assertEqual(stats["current_cache_size"], 0)
        self.assertEqual(stats["cache_misses"], 1)
        self.assertEqual(stats["cache_hits"], 1)

    def test_capacity_must_be_positive_integer(self) -> None:
        for invalid_capacity in (0, -1, 1.5, True):
            with self.subTest(capacity=invalid_capacity):
                with self.assertRaises(ValueError):
                    FileCache(capacity=invalid_capacity)


class SampleFileTests(unittest.TestCase):
    def test_sample_files_are_created_without_overwriting_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            alpha = directory / "sample_alpha.txt"
            alpha.write_text("user content", encoding="utf-8")

            created = create_sample_files(directory)

            self.assertEqual(len(created), len(SAMPLE_FILES))
            self.assertEqual(alpha.read_text(encoding="utf-8"), "user content")
            for sample_path in created:
                self.assertTrue(sample_path.is_file())


if __name__ == "__main__":
    unittest.main()
