"""A small doubly linked list used to track cache recency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class Node:
    """A list entry containing a key and its associated value."""

    key: str
    value: str
    previous: Optional["Node"] = None
    next: Optional["Node"] = None


class DoublyLinkedList:
    """Maintain entries from least-recently used to most-recently used."""

    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def append(self, key: str, value: str) -> Node:
        """Append an entry at the most-recently-used end."""
        node = Node(key=key, value=value, previous=self.tail)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1
        return node

    def remove(self, node: Node) -> None:
        """Remove a node from the list."""
        if node.previous is None:
            self.head = node.next
        else:
            node.previous.next = node.next

        if node.next is None:
            self.tail = node.previous
        else:
            node.next.previous = node.previous

        node.previous = None
        node.next = None
        self._size -= 1

    def move_to_end(self, node: Node) -> None:
        """Mark an existing node as the most recently used."""
        if node is self.tail:
            return
        self.remove(node)
        node.previous = self.tail
        node.next = None
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def pop_first(self) -> Optional[Node]:
        """Remove and return the least-recently-used node."""
        if self.head is None:
            return None
        node = self.head
        self.remove(node)
        return node

    def clear(self) -> None:
        """Remove all nodes and release their links."""
        current = self.head
        while current is not None:
            following = current.next
            current.previous = None
            current.next = None
            current = following
        self.head = None
        self.tail = None
        self._size = 0

    def __iter__(self) -> Iterator[Node]:
        """Iterate from least-recently used to most-recently used."""
        current = self.head
        while current is not None:
            yield current
            current = current.next
