from gwpycore import Node
import pytest

@pytest.fixture
def tree_2by2():
    root = Node("root", None)
    root.tool_tip = "root tooltip"
    for i in range(0, 3):
        child = Node(f"child {i}", root)
        child.tool_tip = f"child {i} tooltip"
        root.children.append(child)
        for x in range(0, 3):
            subchild = Node(f"child {i} {x}", child)
            subchild.tool_tip = f"child {i} {x} tooltip"
            child.children.append(subchild)
    return root


def test_position(tree_2by2):
    c0: Node = tree_2by2.dfs_next()
    assert c0.name == "child 0"
    assert c0.position() == 0

    c00: Node = c0.dfs_next()
    assert c00.name == "child 0 0"
    assert c00.position() == 0

    c01: Node = c00.dfs_next()
    assert c01.name == "child 0 1"
    assert c01.position() == 1

    c02: Node = c01.dfs_next()
    assert c02.name == "child 0 2"
    assert c02.position() == 2

    c1: Node = c02.dfs_next()
    assert c1.name == "child 1"
    assert c1.position() == 1
    c10: Node = c1.dfs_next()
    assert c10.name == "child 1 0"
    assert c10.position() == 0
    c11: Node = c10.dfs_next()
    assert c11.name == "child 1 1"
    assert c11.position() == 1
    c12: Node = c11.dfs_next()
    assert c12.name == "child 1 2"
    assert c12.position() == 2

    c2: Node = c12.dfs_next()
    assert c2.name == "child 2"
    assert c2.position() == 2
    c20: Node = c2.dfs_next()
    assert c20.name == "child 2 0"
    assert c20.position() == 0
    c21: Node = c20.dfs_next()
    assert c21.name == "child 2 1"
    assert c21.position() == 1
    c22: Node = c21.dfs_next()
    assert c22.name == "child 2 2"
    assert c22.position() == 2
