# Formatting

The `.format()` method allows you to generate lists of strings based on a template, which is particularly useful for creating shell commands.

## Basic Usage
Provide a template string containing the `{host}` placeholder:
```python
from hostlist import Hostlist
hl = Hostlist.expand("node[1-3]")

commands = hl.format("ssh {host} 'uptime'")
# Result:
# [
#   "ssh node1 'uptime'",
#   "ssh node2 'uptime'",
#   "ssh node3 'uptime'"
# ]
```

## Common Use Cases
This is ideal for generating scripts or command-line arguments:
```python
# Generating a list of target nodes for a tool
targets = hl.format("--node {host}")
# ["--node node1", "--node node2", "--node node3"]
```
