from gwpycore.gw_data.gw_tree_tools import add_child, dfs_next
from gwpycore.gw_gui.gw_gui_tree_node import GuiTreeNode

import pytest

@pytest.fixture
def tree_2by2():
    root: GuiTreeNode = GuiTreeNode("root", None)
    root.tool_tip = "root tooltip"
    for i in range(0, 3):
        child = GuiTreeNode(f"child {i}", root)
        child.tool_tip = f"child {i} tooltip"
        add_child(root,child)
        for x in range(0, 3):
            subchild = GuiTreeNode(f"child {i} {x}", child)
            subchild.tool_tip = f"child {i} {x} tooltip"
            add_child(child,subchild)
    return root


def test_position(tree_2by2):
    c0: GuiTreeNode = dfs_next(tree_2by2)
    assert c0.name == "child 0"
    assert c0.position() == 0

    c00: GuiTreeNode = dfs_next(c0)
    assert c00.name == "child 0 0"
    assert c00.position() == 0

    c01: GuiTreeNode = dfs_next(c00)
    assert c01.name == "child 0 1"
    assert c01.position() == 1

    c02: GuiTreeNode = dfs_next(c01)
    assert c02.name == "child 0 2"
    assert c02.position() == 2

    c1: GuiTreeNode = dfs_next(c02)
    assert c1.name == "child 1"
    assert c1.position() == 1
    c10: GuiTreeNode = dfs_next(c1)
    assert c10.name == "child 1 0"
    assert c10.position() == 0
    c11: GuiTreeNode = dfs_next(c10)
    assert c11.name == "child 1 1"
    assert c11.position() == 1
    c12: GuiTreeNode = dfs_next(c11)
    assert c12.name == "child 1 2"
    assert c12.position() == 2

    c2: GuiTreeNode = dfs_next(c12)
    assert c2.name == "child 2"
    assert c2.position() == 2
    c20: GuiTreeNode = dfs_next(c2)
    assert c20.name == "child 2 0"
    assert c20.position() == 0
    c21: GuiTreeNode = dfs_next(c20)
    assert c21.name == "child 2 1"
    assert c21.position() == 1
    c22: GuiTreeNode = dfs_next(c21)
    assert c22.name == "child 2 2"
    assert c22.position() == 2
