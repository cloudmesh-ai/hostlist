import re
from dataclasses import dataclass
from typing import Iterable, Union

# ----------------------------------------------------------------------
# Private helpers
# ----------------------------------------------------------------------
_node_pat = re.compile(
    r"""(?P<prefix>[\w-]+?)   # hostname prefix (letters, digits, _ or -)
        (?P<num>\d+)         # numeric part
        (?P<suffix>.*)       # optional suffix (e.g. .domain)
    """,
    re.VERBOSE,
)

def _parse_node(host: str) -> tuple[str, int, str]:
    """Parse a hostname into (prefix, number, suffix)."""
    m = _node_pat.fullmatch(host)
    if not m:
        raise ValueError(f"Cannot parse host: {host!r}")
    return m.group("prefix"), int(m.group("num")), m.group("suffix")

def _group_by_prefix(nodes: Iterable[str]) -> dict[tuple[str, str], list[int]]:
    """Group numbers by (prefix, suffix)."""
    groups: dict[tuple[str, str], list[int]] = {}
    for n in nodes:
        p, num, s = _parse_node(n)
        groups.setdefault((p, s), []).append(num)
    return groups

def _compress_numbers(nums: list[int], pad: int = 0) -> str:
    """Compress a sorted list of ints → ``1-3,5,07-09``."""
    if not nums:
        return ""
    parts = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        # close the current run
        if start == prev:
            parts.append(f"{str(start).zfill(pad)}")
        else:
            parts.append(f"{str(start).zfill(pad)}-{str(prev).zfill(pad)}")
        start = prev = n
    # tail
    if start == prev:
        parts.append(f"{str(start).zfill(pad)}")
    else:
        parts.append(f"{str(start).zfill(pad)}-{str(prev).zfill(pad)}")
    return ",".join(parts)

def _expand_range(range_str: str) -> list[int]:
    """Turn ``1-3,5,07-09`` into a list of ints."""
    result = []
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                a, b = part.split("-", 1)
                result.extend(range(int(a), int(b) + 1))
            except ValueError as e:
                raise ValueError(f"Invalid range in hostlist: {part!r}") from e
        else:
            try:
                result.append(int(part))
            except ValueError as e:
                raise ValueError(f"Invalid number in hostlist: {part!r}") from e
    return result

def _coerce(v: Union["Hostlist", str, list[str]]) -> "Hostlist":
    """Turn any accepted input into a Hostlist."""
    if isinstance(v, Hostlist):
        return v
    if isinstance(v, list):
        return Hostlist.from_list(v)
    if isinstance(v, str):
        return Hostlist.expand(v)
    raise TypeError(f"Cannot coerce {type(v)} to Hostlist")

# ----------------------------------------------------------------------
# Core public API
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Hostlist:
    """Slurm‑style hostlist handling."""
    hosts: tuple[str, ...]

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def expand(cls, spec: str) -> "Hostlist":
        """Parse a possibly‑compressed hostlist string."""
        if not spec:
            return cls(())

        # split on commas that are **outside** brackets
        parts, buf, depth = [], "", 0
        for ch in spec:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth < 0:
                    raise ValueError("Unexpected closing bracket ']' in hostlist")
            if ch == "," and depth == 0:
                parts.append(buf)
                buf = ""
            else:
                buf += ch
        
        if depth != 0:
            raise ValueError("Unclosed bracket '[' in hostlist")
            
        if buf:
            parts.append(buf)

        expanded: list[str] = []
        for token in parts:
            token = token.strip()
            if not token:
                continue
            m = re.fullmatch(
                r"(?P<prefix>[\w-]+)\[(?P<body>[^\]]*)\](?P<suffix>.*)", token
            )
            if not m:               # plain host (no brackets)
                expanded.append(token)
                continue

            prefix, body, suffix = m.group("prefix"), m.group("body"), m.group("suffix")

            # Determine zero‑padding width from the first numeric token
            pad = 0
            for sub in body.split(","):
                sub = sub.strip()
                if not sub: continue
                start = sub.split("-", 1)[0] if "-" in sub else sub
                if start.lstrip("0") != start:          # leading zeros present
                    pad = max(pad, len(start))

            try:
                for num in _expand_range(body):
                    expanded.append(f"{prefix}{str(num).zfill(pad)}{suffix}")
            except ValueError as e:
                raise ValueError(f"Invalid range in bracket for {token!r}: {e}")

        # Normalise ordering (numeric order per prefix/suffix)
        expanded.sort(key=lambda h: _parse_node(h))
        return cls(tuple(expanded))

    @classmethod
    def from_list(cls, hosts: Iterable[str]) -> "Hostlist":
        """Create a Hostlist from an already‑expanded iterable."""
        # Convert to set to remove duplicates, then sort and tuple
        sorted_hosts = sorted(set(hosts), key=lambda h: _parse_node(h))
        return cls(tuple(sorted_hosts))


    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------
    def compact(self, compress: bool = True) -> str:
        """Return a comma‑separated hostlist; optionally compress it."""
        if not self.hosts:
            return ""
        if not compress:
            return ",".join(self.hosts)

        groups = _group_by_prefix(self.hosts)
        parts = []
        # Sort groups to keep output consistent
        for (prefix, suffix) in sorted(groups.keys()):
            nums = groups[(prefix, suffix)]
            nums.sort()
            # infer padding width from the first occurrence of this prefix/suffix
            first = next(
                h for h in self.hosts if h.startswith(prefix) and h.endswith(suffix)
            )
            # extract numeric part for padding
            num_match = re.search(rf"{re.escape(prefix)}(?P<num>\d+){re.escape(suffix)}", first)
            if not num_match:
                continue
            pad = len(num_match.group("num"))
            comp = _compress_numbers(nums, pad=pad)
            parts.append(f"{prefix}[{comp}]{suffix}")
        return ",".join(parts)

    # ------------------------------------------------------------------
    # Set‑like operations (return new Hostlist instances)
    # ------------------------------------------------------------------
    def _as_set(self) -> set[str]:
        return set(self.hosts)

    def diff(self, *others: Union["Hostlist", str, list[str]]) -> "Hostlist":
        """self – union(others)"""
        base = self._as_set()
        for o in others:
            base.difference_update(_coerce(o)._as_set())
        return Hostlist.from_list(sorted(base, key=lambda h: _parse_node(h)))

    def intersect(self, *others: Union["Hostlist", str, list[str]]) -> "Hostlist":
        base = self._as_set()
        for o in others:
            base.intersection_update(_coerce(o)._as_set())
        return Hostlist.from_list(sorted(base, key=lambda h: _parse_node(h)))

    def union(self, *others: Union["Hostlist", str, list[str]]) -> "Hostlist":
        base = self._as_set()
        for o in others:
            base.update(_coerce(o)._as_set())
        return Hostlist.from_list(sorted(base, key=lambda h: _parse_node(h)))

    def xor(self, *others: Union["Hostlist", str, list[str]]) -> "Hostlist":
        base = self._as_set()
        for o in others:
            base.symmetric_difference_update(_coerce(o)._as_set())
        return Hostlist.from_list(sorted(base, key=lambda h: _parse_node(h)))

    # ------------------------------------------------------------------
    # Collection API (Magic Methods)
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.hosts)

    def __iter__(self):
        return iter(self.hosts)

    def __contains__(self, item: object) -> bool:
        return item in self.hosts

    def __getitem__(self, index: Union[int, slice]) -> Union[str, "Hostlist"]:
        """Supports 0-based indexing and slicing."""
        if isinstance(index, slice):
            return Hostlist.from_list(self.hosts[index])
        return self.hosts[index]

    def __repr__(self) -> str:
        return f"Hostlist({self.hosts!r})"

    # ------------------------------------------------------------------
    # Set Operators
    # ------------------------------------------------------------------
    def __and__(self, other: Union["Hostlist", str, list[str]]) -> "Hostlist":
        return self.intersect(other)

    def __or__(self, other: Union["Hostlist", str, list[str]]) -> "Hostlist":
        return self.union(other)

    def __sub__(self, other: Union["Hostlist", str, list[str]]) -> "Hostlist":
        return self.diff(other)

    def __xor__(self, other: Union["Hostlist", str, list[str]]) -> "Hostlist":
        return self.xor(other)

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------
    def nth(self, n: int) -> str:
        """Return the n‑th host (1‑based)."""
        if n < 1 or n > len(self):
            raise ValueError("index out of range")
        return self[n - 1]

    def find(self, host: str) -> int:
        """Return 1‑based position of *host*."""
        try:
            return self.hosts.index(host) + 1
        except ValueError:
            raise ValueError("host not found") from None

    def count(self) -> int:
        """Backward compatible with __len__."""
        return len(self)

    def remove(self, host: str) -> "Hostlist":
        """Return a new Hostlist without *host*."""
        if host not in self:
            raise ValueError("host not found")
        new = [h for h in self.hosts if h != host]
        return Hostlist.from_list(new)

    def delimiter(self, d: str) -> str:
        """Join the list with a custom delimiter (no compression)."""
        return d.join(self.hosts)

    def size(self, N: int) -> "Hostlist":
        """Return at most N hosts (negative → last N)."""
        return Hostlist.from_list(self.hosts[:N] if N >= 0 else self.hosts[N:])

    def exclude(self, *hosts: str) -> "Hostlist":
        """Return a Hostlist without the supplied hosts."""
        remaining = [h for h in self.hosts if h not in hosts]
        if not remaining:
            raise ValueError("resulting hostlist empty")
        return Hostlist.from_list(remaining)

    def quiet(self) -> str:
        """Plain comma‑separated list; raise if empty."""
        if not self.hosts:
            raise ValueError("hostlist empty")
        return ",".join(self.hosts)

    def format(self, template: str) -> list[str]:
        """
        Return a list of formatted strings using the provided template.
        The template should contain a {host} placeholder.
        """
        return [template.format(host=h) for h in self.hosts]


# ----------------------------------------------------------------------
