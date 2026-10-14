# Data Structures — Lecture Notes

## Arrays
An array is a fixed-size collection of elements of the same type stored in contiguous memory.
- **Random access**: O(1) — access any element by index instantly
- **Search**: O(n) — must scan each element in the worst case
- **Insertion/Deletion**: O(n) — shifting elements is required
- Best used when you know the size in advance and need fast lookups by index

## Linked Lists
A linked list is a dynamic data structure where each element (node) stores a value and a pointer to the next node.

### Singly Linked List
- Each node has: `data` and `next` pointer
- **Insertion at head**: O(1)
- **Search**: O(n)
- **No random access** — must traverse from head

### Doubly Linked List
- Each node has: `data`, `next`, and `prev` pointers
- Allows traversal in both directions
- Used in: browser history, undo/redo, music playlists

## Stacks
A stack is a Last-In-First-Out (LIFO) data structure.
- **push(x)**: add to top — O(1)
- **pop()**: remove from top — O(1)
- **peek()**: view top without removing — O(1)
- Used in: function call stacks, expression parsing, backtracking algorithms

## Queues
A queue is a First-In-First-Out (FIFO) data structure.
- **enqueue(x)**: add to rear — O(1)
- **dequeue()**: remove from front — O(1)
- Used in: task scheduling, BFS graph traversal, print spooling

## Binary Search Trees (BST)
A BST is a tree where for every node:
- Left subtree contains only nodes with values **less than** the node
- Right subtree contains only nodes with values **greater than** the node

Average case (balanced):
- **Search**: O(log n)
- **Insert**: O(log n)
- **Delete**: O(log n)

Worst case (degenerate/skewed tree):
- All operations: O(n)

## Hash Tables
A hash table maps keys to values using a hash function.
- **Insert / Search / Delete**: O(1) average, O(n) worst case (many collisions)
- Collisions handled by: chaining (linked lists) or open addressing (probing)
- Load factor = n/m (number of keys / number of buckets) — keep below 0.7 for performance

## Big-O Complexity Summary

| Structure      | Access | Search | Insert | Delete |
|----------------|--------|--------|--------|--------|
| Array          | O(1)   | O(n)   | O(n)   | O(n)   |
| Linked List    | O(n)   | O(n)   | O(1)*  | O(1)*  |
| Stack          | O(n)   | O(n)   | O(1)   | O(1)   |
| Queue          | O(n)   | O(n)   | O(1)   | O(1)   |
| BST (avg)      | -      | O(log n)| O(log n)| O(log n)|
| Hash Table     | -      | O(1)   | O(1)   | O(1)   |

*at head/tail with known pointer
