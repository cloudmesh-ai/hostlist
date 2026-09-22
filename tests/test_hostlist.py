import pytest
from hostlist import Hostlist

# ------------------------------------------------------------------
# Expansion & Compression Tests
# ------------------------------------------------------------------

@pytest.mark.parametrize("spec, expanded, compressed", [
    ("node[01-03,07]", "node01,node02,node03,node07", "node[01-03,07]"),
    ("node[1-3,5]", "node1,node2,node3,node5", "node[1-3,5]"),
    ("node[10-12]", "node10,node11,node12", "node[10-12]"),
    ("node[001-002]", "node001,node002", "node[001-002]"),
    ("node1,node3,node2", "node1,node2,node3", "node[1-3]"),
    ("node[1-3],gpu[1-2]", "gpu1,gpu2,node1,node2,node3", "gpu[1-2],node[1-3]"),
    ("node[1-3].domain", "node1.domain,node2.domain,node3.domain", "node[1-3].domain"),
    ("node[1-3],headnode", "headnode,node1,node2,node3", "headnode,node[1-3]"),
    ("headnode,node[1-3]", "headnode,node1,node2,node3", "headnode,node[1-3]"),
    ("node[1-3],gpu[1-2],special-srv", "gpu1,gpu2,node1,node2,node3,special-srv", "gpu[1-2],node[1-3],special-srv"),
    ("", "", ""),
])
def test_expansion_and_compression(spec, expanded, compressed):
    hl = Hostlist.expand(spec)
    assert hl.compact(compress=False) == expanded
    assert hl.compact() == compressed

# ------------------------------------------------------------------
# Set Operations Tests
# ------------------------------------------------------------------

def test_set_methods():
    a = Hostlist.expand("node[1-5]")
    b = Hostlist.expand("node[4-8]")
    
    assert a.diff(b).compact() == "node[1-3]"
    assert a.intersect(b).compact() == "node[4-5]"
    assert a.union(b).compact() == "node[1-8]"
    assert a.xor(b).compact() == "node[1-3,6-8]"

def test_set_operators():
    a = Hostlist.expand("node[1-5]")
    b = Hostlist.expand("node[4-8]")
    
    assert (a - b).compact() == "node[1-3]"
    assert (a & b).compact() == "node[4-5]"
    assert (a | b).compact() == "node[1-8]"
    assert (a ^ b).compact() == "node[1-3,6-8]"

def test_set_coercion():
    # Test that set operations work with strings and lists
    hl = Hostlist.expand("node[1-3]")
    
    assert (hl | "node4").compact() == "node[1-4]"
    assert (hl | ["node4", "node5"]).compact() == "node[1-5]"
    assert (hl - "node1").compact() == "node[2-3]"

# ------------------------------------------------------------------
# Collection API Tests
# ------------------------------------------------------------------

def test_collection_basics():
    hl = Hostlist.expand("node[1-3]")
    
    assert len(hl) == 3
    assert hl.count() == 3
    assert list(hl) == ["node1", "node2", "node3"]
    assert "node1" in hl
    assert "node4" not in hl
    assert hl[0] == "node1"
    assert hl[2] == "node3"
    # Verify repr
    assert "Hostlist" in repr(hl)
    assert "node1" in repr(hl)

def test_slicing():
    hl = Hostlist.expand("node[1-10]")
    
    assert hl[0:3].compact() == "node[1-3]"
    assert hl[7:].compact() == "node[8-10]"
    assert hl[:2].compact() == "node[1-2]"
    assert hl[0:10:2].compact(compress=False) == "node1,node3,node5,node7,node9"
    assert hl[-3:].compact() == "node[8-10]"

def test_immutability():
    hl = Hostlist.expand("node[1-2]")
    # Should be hashable
    assert hl in {hl}
    
    with pytest.raises(AttributeError):
        hl.hosts = ("node1",) # type: ignore

# ------------------------------------------------------------------
# Misc Helpers Tests
# ------------------------------------------------------------------

def test_misc_helpers():
    hl = Hostlist.expand("node[1-10]")
    
    assert hl.nth(2) == "node2"
    assert hl.find("node2") == 2
    assert hl.size(3).compact() == "node[1-3]"
    assert hl.size(-2).compact() == "node[9-10]"
    assert hl.delimiter(";").startswith("node1;node2")
    
    # Test remove
    assert hl.remove("node1").compact() == "node[2-10]"
    
    # Test exclude
    assert hl.exclude("node1", "node10").compact() == "node[2-9]"
    
    # Test quiet
    assert hl.quiet() == "node1,node2,node3,node4,node5,node6,node7,node8,node9,node10"

# ------------------------------------------------------------------
# Error Handling & Edge Cases
# ------------------------------------------------------------------

def test_parsing_errors():
    with pytest.raises(ValueError, match="Unclosed bracket"):
        Hostlist.expand("node[1-3")
    
    with pytest.raises(ValueError, match="Unexpected closing bracket"):
        Hostlist.expand("node]1-3[")
        
    with pytest.raises(ValueError, match="Invalid range in bracket"):
        Hostlist.expand("node[1-a]")

def test_empty_and_singletons():
    # Empty
    hl_empty = Hostlist.expand("")
    assert len(hl_empty) == 0
    assert hl_empty.compact() == ""
    with pytest.raises(ValueError, match="hostlist empty"):
        hl_empty.quiet()
        
    # Singleton
    hl_one = Hostlist.expand("node1")
    assert len(hl_one) == 1
    assert hl_one.compact() == "node[1]"

def test_from_list_behavior():
    # Test deduplication and sorting
    hosts = ["node3", "node1", "node2", "node1"]
    hl = Hostlist.from_list(hosts)
    assert list(hl) == ["node1", "node2", "node3"]
    assert len(hl) == 3

def test_formatting():
    hl = Hostlist.expand("node[1-3]")
    
    # Basic formatting
    assert hl.format("ssh {host} 'uptime'") == [
        "ssh node1 'uptime'",
        "ssh node2 'uptime'",
        "ssh node3 'uptime'",
    ]
    
    # Different template
    assert hl.format("{host}.domain") == [
        "node1.domain",
        "node2.domain",
        "node3.domain",
    ]
    
    # Empty hostlist
    hl_empty = Hostlist.expand("")
    assert hl_empty.format("ssh {host}") == []
