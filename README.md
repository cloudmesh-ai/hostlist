# Hostlist

A clean, modern, and fully‑typed Python library for parsing and manipulating Slurm‑style hostlists.

## Features

* Parses both plain and compressed Slurm‑style hostlists.
* Expands them to a sorted list of hostnames.
* Offers set‑like operations (`diff`, `intersect`, `union`, `xor`).
* Provides handy helpers (`nth`, `find`, `count`, `remove`, `delimiter`, `size`, `exclude`, `quiet`).
* **Template Formatting**: Generate a list of strings (e.g., shell commands) for all hosts.
* **CLI Tools**: Expand and compact hostlists directly from the shell.
* Can return either an **expanded** comma‑separated string or a **compressed** representation.

## Installation

```bash
pip install .
```

## Usage

### Python API

```python
from hostlist import Hostlist

# create a Hostlist from a compressed string
hl = Hostlist.expand("node[01-03,07],gpu[1-2]")

print("Expanded:", hl.compact(compress=False))
# → Expanded: gpu1,gpu2,node01,node02,node03,node07

print("Compressed:", hl.compact())
# → Compressed: gpu[1-2],node[01-03,07]

# set‑operations
other = Hostlist.expand("node[02-04],gpu[2]")
print("Diff:", hl.diff(other).compact())
# → Diff: gpu[1],node[01,03,07]

# Template formatting
cmds = hl.format("ssh {host} 'hostname'")
# → ["ssh gpu1 'hostname'", "ssh gpu2 'hostname'", ...]
```

### Command Line Interface

After installing the package, you can use the following commands:

**Expand a compressed list:**
```bash
hostlist-expand "node[01-03],gpu[1-2]"
# → gpu1,gpu2,node01,node02,node03,node07
```

**Compact an expanded list:**
```bash
hostlist-compact "node1,node2,node3"
# → node[1-3]
```

**General utility:**
```bash
hostlist expand "node[01-03]"
# → node01,node02,node03
```
