# Custom LRU-Based File Cache Simulator

A menu-driven Python command-line program that caches text files using a
least-recently-used (LRU) eviction policy.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Run

From this project directory:

```bash
python main.py
```

The program creates four example text files in `sample_files/` the first time
it runs. Existing sample files are left unchanged. The default cache capacity
is three files.

## Menu

1. **Open File** — read a UTF-8 text file from disk and add it to the cache.
   Opening an already cached file counts as a hit and refreshes its LRU position.
2. **Read File** — display the contents of a file already in the cache. This
   also counts as a hit and refreshes its LRU position. A file that is not
   cached must first be opened.
3. **Display Cached Files** — show the cache from least recently used to most
   recently used.
4. **Search File in Cache** — search cached filenames, ignoring letter case.
5. **Show Cache Statistics** — show hits, misses, current occupancy, capacity,
   and evictions.
6. **Clear Cache** — remove all cached contents. Cumulative counters are kept.
7. **Exit** — leave the program.

## Demonstrate LRU eviction

The cache can hold three files by default. Choose **Open File** and enter these
paths in order:

```text
sample_files/sample_alpha.txt
sample_files/sample_bravo.txt
sample_files/sample_charlie.txt
```

Now open `sample_files/sample_alpha.txt` again to make alpha the most recently
used file. Open `sample_files/sample_delta.txt`. Bravo is now the least
recently used file, so it is evicted. Choose **Display Cached Files** to see
the remaining order:

```text
sample_charlie.txt
sample_alpha.txt
sample_delta.txt
```

This also increases **Evicted Files Count** by one.

## Implementation

- `file_cache.py` contains the `FileCache` class, statistics, file loading,
  searching, and LRU eviction.
- `doubly_linked_list.py` provides the linked list used to maintain recency.
- The dictionary maps each normalized absolute file path to its linked-list
  node. The list stores entries from LRU (head) to MRU (tail), allowing cache
  lookups and recency updates in O(1) time.
- `main.py` creates the sample files and runs the interactive menu.
- `test_cache.py` covers cache behavior, list operations, sample-file setup,
  statistics, and eviction.

Statistics count cache lookups: opening a cached file is a hit, and trying to
read an uncached path is a miss. Opening a path that is not on disk is also
counted as a miss. Clearing the cache preserves the counters for the current
program session.

## Run tests

```bash
python -m unittest -v
```
