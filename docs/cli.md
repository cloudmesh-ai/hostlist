# CLI Tool

The `hostlist` command-line tool provides a quick way to expand and compact hostlists from the terminal.

## Expand
Expand a compressed specification into a list of hosts.

```bash
# Basic expansion
hostlist expand "node[01-03,07]"
# Output: node01,node02,node03,node07

# Quiet output (comma-separated)
hostlist expand "node[1-3]" --quiet
# Output: node1,node2,node3

# Formatted output
hostlist expand "node[1-3]" --format "ssh {host} uptime"
# Output:
# ssh node1 uptime
# ssh node2 uptime
# ssh node3 uptime
```

## Compact
Take a list of hostnames and compress them into Slurm style.

```bash
hostlist compact "node1,node2,node3,node7"
# Output: node[1-3,7]
```

## Pipeline Support
The CLI supports reading from `stdin`, allowing it to be used in pipelines:

```bash
echo "node[1-3]" | hostlist expand
```
