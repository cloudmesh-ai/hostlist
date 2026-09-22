# Collection API

A `Hostlist` object behaves like a read-only sequence of hostnames, providing several useful collection-based methods.

## Indexing and Slicing
You can access hosts by index or take a slice of the hostlist:
```python
hl = Hostlist.expand("node[1-10]")

# Get the first host
print(hl[0]) # "node1"

# Get a slice (returns a new Hostlist)
sub_hl = hl[0:3] 
print(sub_hl.compact()) # "node[1-3]"
```

## Position and Search
*   **`nth(n)`**: Returns the $n$-th host (1-based indexing).
*   **`find(host)`**: Returns the 1-based position of a specific host.

```python
hl = Hostlist.expand("node[1-10]")
print(hl.nth(2))      # "node2"
print(hl.find("node2")) # 2
```

## Size and Filtering
*   **`size(N)`**: Returns a new `Hostlist` containing at most $N$ hosts. Use negative numbers to get the last $N$ hosts.
*   **`exclude(*hosts)`**: Returns a new `Hostlist` with the specified hosts removed.

```python
hl = Hostlist.expand("node[1-10]")
print(hl.size(3).compact())    # "node[1-3]"
print(hl.size(-2).compact())   # "node[9-10]"
print(hl.exclude("node1").compact()) # "node[2-10]"
```

## Iteration and Length
`Hostlist` supports standard Python collection protocols:
```python
hl = Hostlist.expand("node[1-3]")
print(len(hl)) # 3
for host in hl:
    print(host)
```
