"""Menu-driven command line interface for the LRU file-cache simulator."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from file_cache import CachedFile, FileCache, FileNotCachedError


DEFAULT_CAPACITY = 3
SAMPLE_FILES = {
    "sample_alpha.txt": (
        "Alpha sample file\n"
        "This file is generated automatically for the LRU cache demo.\n"
    ),
    "sample_bravo.txt": (
        "Bravo sample file\n"
        "Open the sample files in order to see older entries evicted.\n"
    ),
    "sample_charlie.txt": (
        "Charlie sample file\n"
        "Reading a cached file makes it the most recently used entry.\n"
    ),
    "sample_delta.txt": (
        "Delta sample file\n"
        "With the default capacity of three, this file evicts the LRU entry.\n"
    ),
}


def create_sample_files(directory: Optional[Path] = None) -> list[Path]:
    """Create demo text files without overwriting any existing user files."""
    sample_directory = directory or Path(__file__).resolve().parent / "sample_files"
    sample_directory.mkdir(parents=True, exist_ok=True)

    created_files = []
    for filename, contents in SAMPLE_FILES.items():
        sample_path = sample_directory / filename
        if not sample_path.exists():
            sample_path.write_text(contents, encoding="utf-8")
        created_files.append(sample_path)
    return created_files


def _display_file_list(files: list[CachedFile]) -> None:
    if not files:
        print("No files are currently cached.")
        return

    print("Cached files (LRU → MRU):")
    for index, cached_file in enumerate(files, start=1):
        print(
            f"  {index}. {cached_file.path.name} "
            f"({cached_file.size_bytes} bytes) — {cached_file.path}"
        )


def _read_input(prompt: str) -> Optional[str]:
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nInput ended. Exiting.")
        return None


def _open_file(cache: FileCache) -> None:
    raw_path = _read_input("File path (or sample_files/sample_alpha.txt): ")
    if raw_path is None:
        return
    if not raw_path:
        print("Please enter a file path.")
        return

    try:
        contents = cache.open_file(raw_path)
    except (OSError, UnicodeError) as error:
        print(f"Could not open file: {error}")
        return

    print(f"\nOpened and cached: {Path(raw_path).expanduser().resolve()}")
    print("-" * 60)
    print(contents, end="" if contents.endswith("\n") else "\n")
    print("-" * 60)


def _read_cached_file(cache: FileCache) -> None:
    _display_file_list(cache.list_cached_files())
    raw_path = _read_input("Cached file path or name: ")
    if raw_path is None:
        return
    if not raw_path:
        print("Please enter a file path or name.")
        return

    # A displayed filename is sufficient when it matches one cached item.
    matches = [
        cached_file
        for cached_file in cache.list_cached_files()
        if cached_file.path.name.casefold() == raw_path.casefold()
        or str(cached_file.path).casefold() == raw_path.casefold()
    ]
    selected_path = matches[0].path if len(matches) == 1 else Path(raw_path)

    try:
        contents = cache.read_cached_file(selected_path)
    except FileNotCachedError as error:
        print(f"{error} Use Open File to load it first.")
        return

    print(f"\nCached contents of {selected_path.name}:")
    print("-" * 60)
    print(contents, end="" if contents.endswith("\n") else "\n")
    print("-" * 60)


def _search_cache(cache: FileCache) -> None:
    query = _read_input("Search cached filenames: ")
    if query is None:
        return
    if not query:
        print("Please enter a search term.")
        return

    matches = cache.search_cached_files(query)
    if not matches:
        print(f"No cached files match {query!r}.")
        return
    print(f"Found {len(matches)} matching file(s):")
    _display_file_list(matches)


def _show_statistics(cache: FileCache) -> None:
    stats = cache.get_statistics()
    print("\nCache statistics")
    print("----------------")
    print(f"Cache Hits:          {stats['cache_hits']}")
    print(f"Cache Misses:        {stats['cache_misses']}")
    print(
        f"Current Cache Size:  {stats['current_cache_size']} / "
        f"{stats['capacity']} files"
    )
    print(f"Evicted Files Count: {stats['evicted_files_count']}")


def _show_menu() -> None:
    print(
        "\n=== Custom LRU-Based File Cache Simulator ===\n"
        "1. Open File\n"
        "2. Read File\n"
        "3. Display Cached Files\n"
        "4. Search File in Cache\n"
        "5. Show Cache Statistics\n"
        "6. Clear Cache\n"
        "7. Exit"
    )


def main() -> None:
    """Start the simulator and process menu choices until the user exits."""
    create_sample_files()
    cache = FileCache(capacity=DEFAULT_CAPACITY)

    print("Sample text files are ready in the sample_files/ directory.")
    print(f"Cache capacity: {cache.capacity} files.")
    print("Open four different files to see LRU eviction.")

    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _open_file(cache),
        "2": lambda: _read_cached_file(cache),
        "3": lambda: _display_file_list(cache.list_cached_files()),
        "4": lambda: _search_cache(cache),
        "5": lambda: _show_statistics(cache),
    }

    while True:
        _show_menu()
        choice = _read_input("Choose an option (1-7): ")
        if choice is None or choice == "7":
            print("Goodbye.")
            break
        if choice == "6":
            cache.clear()
            print("Cache cleared. Cumulative statistics have been preserved.")
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
