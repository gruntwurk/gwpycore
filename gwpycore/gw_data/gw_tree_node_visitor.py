from abc import ABC, abstractmethod

from gwpycore.gw_data.gw_tree_node import TreeNode


class TreeNodeVisitor(ABC):
    """
    A tree node visitor needs a tree_depth property so that the
    traverse() method can inform the visitor how deep
    into the tree (branch) it has gone so far.
    """
    tree_depth = 0

    @abstractmethod
    def enter_node(self, node: TreeNode):
        pass

    @abstractmethod
    def exit_node(self, node: TreeNode):
        pass


class XMLTreeNodeVisitor(TreeNodeVisitor):

    def __init__(self):
        self.buf = ""
        self.tree_depth = 0

    def indent(self):
        self.buf += "  " * self.tree_depth

    def open_tag(self, tagName: str):
        self.buf += f"<{tagName}>"

    def close_tag(self, tagName: str):
        self.buf += f"</{tagName}>"

    def enter_node(self, node: TreeNode):
        if node.is_leaf():
            self.indent()
            self.open_tag(node.name)
            if node.payload:
                self.buf += (str(node.payload))
            self.close_tag(node.name)
        else:
            self.indent()
            self.open_tag(node.name)
        self.buf += ("\n")

    def exit_node(self, node: TreeNode):
        self.indent()
        self.close_tag(node.name)
        self.buf += ("\n")

    def clear_buffer(self):
        self.buf = ""
