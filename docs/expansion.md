# Expansion

The `Hostlist.expand()` method converts a Slurm-style compressed hostlist string into a `Hostlist` object containing all individual hostnames.

## Basic Expansion
A simple range is expanded into its constituent hosts:
```python
from hostlist import Hostlist
hl = Hostlist.expand("node[01-03]")
# Result: ["node01", "node02", "node03"]
```

## Multiple Ranges and Individuals
You can combine multiple ranges and individual hosts in a single specification:
```python
hl = Hostlist.expand("node[01-03,07],gpu01")
# Result: ["gpu01", "node01", "node02", "node03", "node07"]
```

## Zero Padding
The library automatically detects the padding width from the specification to preserve leading zeros:
```python
hl = Hostlist.expand("node[001-002]")
# Result: ["node001", "node002"]
```

## Mixed Hostnames
Hostlists can contain a mix of numeric ranges and literal hostnames:
```python
hl = Hostlist.expand("node[1-3],headnode")
# Result: ["headnode", "node1", "node2", "node3"]
```

## Suffixes
Suffixes (like domain names) are preserved during expansion:
```python
hl = Hostlist.expand("node[1-3].cluster.local")
# Result: ["node1.cluster.local", "node2.cluster.local", "node3.cluster.local"]
```
