# Compression

The `compact()` method converts a `Hostlist` object back into a compressed Slurm-style string.

## Basic Compression
A sequence of numeric hosts is compressed into a range:
```python
from hostlist import Hostlist
hl = Hostlist.from_list(["node1", "node2", "node3"])
print(hl.compact()) 
# Output: "node[1-3]"
```

## Mixed Compression
Literal hosts are kept separate, while numeric hosts are grouped and compressed:
```python
hl = Hostlist.from_list(["node1", "node2", "node3", "headnode"])
print(hl.compact())
# Output: "headnode,node[1-3]"
```

## Preservation of Padding
The `compact()` method preserves the padding found in the hosts:
```python
hl = Hostlist.from_list(["node01", "node02", "node03"])
print(hl.compact())
# Output: "node[01-03]"
```

## Uncompressed Output
If you need the hosts as a simple comma-separated list without ranges, use `compress=False`:
```python
print(hl.compact(compress=False))
# Output: "node01,node02,node03"
```
