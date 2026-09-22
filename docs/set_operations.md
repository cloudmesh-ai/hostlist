# Set Operations

The `Hostlist` class supports powerful set operations, allowing you to manipulate groups of hosts using both method calls and Python operators.

## Available Operations

| Operation | Method | Operator | Description |
| :--- | :--- | :--- | :--- |
| **Union** | `.union()` | `\|` | All hosts in either hostlist. |
| **Intersection** | `.intersect()` | `&` | Only hosts present in both hostlists. |
| **Difference** | `.diff()` | `-` | Hosts in the first list but not the second. |
| **Symmetric Diff** | `.xor()` | `^` | Hosts in either list, but not both. |

## Examples

```python
from hostlist import Hostlist
a = Hostlist.expand("node[1-5]")
b = Hostlist.expand("node[4-8]")

# Union: node[1-8]
print((a \| b).compact())

# Intersection: node[4-5]
print((a & b).compact())

# Difference: node[1-3]
print((a - b).compact())

# Symmetric Difference: node[1-3,6-8]
print((a ^ b).compact())
```

## Coercion
Set operations automatically coerce strings or lists into `Hostlist` objects:
```python
hl = Hostlist.expand("node[1-3]")
result = hl \| "node4" # Result: node[1-4]
```
