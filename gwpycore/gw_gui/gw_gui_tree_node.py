from gwpycore.gw_data.gw_tree_node import TreeNode
from gwpycore.gw_data.gw_tree_tools import add_child


class GuiTreeNode(TreeNode):
    """
    A tree node that is compatible with the Qt Tree Model/View (in
    conjuction with QModel Index).

    name -- a (display) name for the node.
    payload -- any object associated with the node.
    parent -- this node's parent node (or None if this is the root node).
    """
    index = None
    widget = None
    tool_tip: str = ""

    def __init__(self, name: str, parent, payload: any = None):
        self.name: str = name
        self.payload: any = payload
        self.parent: TreeNode = parent
        self.first_child: TreeNode = None
        self.last_child: TreeNode = None
        self.next_sibling: TreeNode = None
        if parent:
            add_child(parent,self)

__all__ = ("GuiTreeNode",)