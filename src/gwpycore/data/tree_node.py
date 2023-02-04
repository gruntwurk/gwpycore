from abc import ABC, abstractmethod

__all__ = [
    "TreeNode",
    "TreeNodeVisitor",
    "XMLTreeNodeVisitor",
    "depth_first_traverse",
    "xml_dump",
]

# ############################################################################
#                                                                    TREE NODE
# ############################################################################


class TreeNode:
    # FYI: This is not declared to be a `dataclass` because all of the methods that
    # would automatically be implemented already are.
    """
    A node in a classic tree structure where any node can have zero or more
    children.

    This class can be used directly (with all of the "meat" being contained in
    a payload object), or this class can be subclassed with the addition of
    other fields (besides `name` and `payload`).

    This class features operator overloads as follows:

        `a == b` Equality is based on the node's identifying fields (`name` by default),
                 rather than the object's location in memory.
        `a != b` Same
        `a < b`  `a` is a descendant of `b` (child, grandchild, ...)
        `a <= b` `a` is `b`, or `a` is a descendant of `b` (child, grandchild, ...)
        `a > b`  `a` is an ancestor of `b` (parent, grandparent, ...)
        `a >= b` `a` is `b`, or `a` is an ancestor of `b` (parent, grandparent, ...)

        Be aware that `a < b` and `a >= b` can both be False, meaning they have no
        descendancy relationship at all.

    NOTE: If you subclass this class and add fields, then be sure to reimplement
          the `assign()` method to include them. Also, if any of the added fields
          are significant (identifying) then be sure to reimplement the `__eq__()`
          method as well.

         FIXME
        and have it copy the data appropriately. Also, the factoryCreate() method
        must be overloaded to create the proper descendant class.
    """

    def __init__(self, source, payload: any = None):
        """
        :param source: If `source` is an instance of `TreeNode`, then this new instance
                    be created as a clone of it. Otherwise, source will be cast to a
                    `str` and that string used for the `name` of this new node.
        :param payload: Any object to be associated with the node.
        """
        self.parent = None
        self.first_child = None
        self.last_child = None
        self.next_sibling = None

        if isinstance(source, self.__class__):
            self.assign(source)
        else:
            self.name = str(source)

        if payload:
            self.payload = payload

    def assign(self, source: "TreeNode"):
        self.name = source.name
        self.parent = source.parent
        self.first_child = source.first_child
        self.last_child = source.last_child
        self.next_sibling = source.next_sibling
        self.payload = source.payload

    def __str__(self) -> str:
        name = self.name or ""
        parent_name = self.parent.name if self.parent else ""
        first_child = self.first_child.name if self.first_child else ""
        last_child = self.last_child.name if self.last_child else ""
        next_sibling = self.next_sibling.name if self.next_sibling else ""
        return f"(name = {name}, parent = {parent_name}, first_child = {first_child}, last_child = {last_child}, next_sibling = {next_sibling})"

    def is_leaf(self) -> bool:
        """
        Whether or not self is a leaf node (i.e. True if the node has no children).
        """
        return self.first_child is None

    def child_count(self) -> int:
        """
        The number of children that belong to this node.
        """
        child = self.first_child
        result = 0
        while child is not None:
            result += 1
            child = child.next_sibling
        return result

    def position(self):
        """
        Which child am I? (0 = the eldest)
        """
        position = 0
        if self.parent:
            child = self.parent.first_child
            while child and child != self:
                position += 1
                child = child.next_sibling
        return position

    def is_only_child(self) -> bool:
        """
        Whether of not this node has a parent and this node is that parent's only child.
        """
        if self.parent is None:
            return False
        return self.parent.first_child == self.parent.last_child

    def first_leaf_node(self) -> "TreeNode":
        """
        Determines the first leaf node of self node. If self node is already a
        leaf node, then "self" is returned. Otherwise, self node's first child is
        returned -- or its first grandchild, or whatever is the deepest first
        child that can be found. Usually used with the head node to find the
        starting point for a depth-first-search.
        """
        result = self
        while not result.isLeaf():
            result = result.first_child
        return result

    def sibling(self):
        """
        Who is my next younger sibling? (or None)
        """
        return self.next_sibling

    def previous_sibling(self) -> "TreeNode":
        """
        Finds the sibling that refers to this node as its next sibling.
        Returns None if this node is the first child.
        (Not necessarily very fast.)
        """
        if not self.parent:
            return None
        result = self.parent.first_child
        if result == self:
            return None
        while (result.next_sibling is not None) and (result.next_sibling is not self):
            result = result.next_sibling
        return result

    def get_child(self, position):
        result = self.first_child
        for _ in range(position + 1):
            if not result:
                break
            result = result.next_sibling
        return result

    def add_child(self, child_node: "TreeNode"):
        """
        Adds the given node into the tree as a child of this node (becoming the "last child").
        """
        child_node.parent = self
        if self.is_leaf():
            self.first_child = child_node
        else:
            self.last_child.next_sibling = child_node
        self.last_child = child_node

    def add_sibling(self, other):
        """
        Adds the given `other` node into the tree as the immediate next sibling
        of this node.
        """
        if self.parent:
            self.parent.add_child(other)

    def insert_sibling(self, other, before=True):
        """
        Inserts the given `other` node into the tree as an immediate sibling of
        this node, either before or after.
        """
        other.parent = self.parent
        if before:
            prev_sib = self.previous_sibling()
            other.next_sibling = self
            if prev_sib:
                prev_sib.next_sibling = other
            else:
                self.parent.first_child = other
        else:
            # Cannot just call add_sibling here because that would add it to
            # the end (as the youngest sibling), rather that as the immediate
            # next sibling.
            other.next_sibling = self.next_sibling
            self.next_sibling = other

    def insert_parent(self, other):
        """
        Inserts the given `other` node into the tree in place of this
        node, with this node becoming a child of the new node.
        """
        # First, insert the node as a sibling, then move this node to become a child (the only child) of it.
        self.insert_sibling(other)
        other.next_sibling = self.next_sibling
        if other.next_sibling is None:
            other.parent.last_child = other
        self.next_sibling = None
        other.first_child = self
        other.last_child = self
        self.parent = other

    def split_branch(self):
        """
        Split the current branch between this node and its previous (older) sibling(s).
        This node, along with any following (younger) siblings are moved to their own branch
        with a new parent (a clone of the old parent).
        NOTE: Be sure to rename one of the two parents.

        Nothing happens if this node is the first (oldest) child.
        """
        if self.parent.first_child is self:
            return
        prev = self.previous_sibling()
        parent_clone = TreeNode(self.parent)
        self.parent.insert_sibling(parent_clone, before=False)
        parent_clone.last_child = self.parent.last_child
        parent_clone.first_child = self
        self.parent = parent_clone
        prev.next_sibling = None

        younger_sibling = self.next_sibling
        while younger_sibling:
            younger_sibling.parent = parent_clone
            younger_sibling = younger_sibling.next_sibling

    def remove_parent(self):
        """
        Promote self node, along with any and all siblings to the level of its
        parent, replacing the parent.
        """
        original_parent: TreeNode = self.parent
        grandparent: TreeNode = original_parent.parent

        # Change this node and all of its siblings to claim the grandparent as their  parent.
        child: TreeNode = original_parent.first_child
        while child is not None:
            child.parent = grandparent
            child = child.next_sibling

        # Link the first grandchild to the original parent's previous sibling
        if grandparent:
            if grandparent.first_child == original_parent:
                grandparent.first_child = original_parent.first_child
            else:
                original_parent.previous_sibling().next_sibling = (
                    original_parent.first_child
                )

        # Link the last grandchild to the original parent's next sibling
        if original_parent.next_sibling:
            original_parent.last_child.next_sibling = original_parent.next_sibling
        elif grandparent:
            grandparent.last_child = original_parent.last_child
        # Clear the original parent's references to its children.
        original_parent.last_child = None
        original_parent.first_child = None

    def simplify_parentage(self):
        """
        If this node is an only child, it will be promoted to take over for its
        parent. If that makes it the only child of the grandparent, it is
        promoted again, ad infinitum.
        """
        while self.is_only_child():
            self.remove_parent()

    def dfs_next(self, root_of_search=None):
        """
        Who is the next node in Depth-First-Search order?

        :param root_of_search: Stops searching when the DFS gets back to this node.

        :return: The next node, or `None` if the search is exhausted.
        """
        if self.first_child:
            return self.first_child

        if self.next_sibling:
            return self.next_sibling

        ancestor = self.parent
        while ancestor is not None and ancestor is not root_of_search:
            if ancestor.next_sibling:
                return ancestor.next_sibling
            ancestor = ancestor.parent
        return None

    def find_ancestor(self, other: "TreeNode") -> int:
        """
        Looks to see if `other` is an ancestor of this node. If so, it returns
        the number of generations back that `other` was found. That is, 0 means
        that this node is the node being sought, 1 means that `other` is this
        node's parent, 2 = grandparent, etc.

        :param other: A `TreeNode` instance that equates to the ancestor being
                      sought (according to the `__eq__` implementation).
        :return: `None` if `other` is not an ancestor (or `other` is `None`); otherwise, 0 = self,
                 1 = parent, 2 = grandparent,...
        """
        if other is None:
            return None
        node = self
        distance = 0
        while node is not None:
            if node == other:
                return distance
            node = node.parent
            distance += 1
        return None

    def is_ancestor(self, other: "TreeNode") -> bool:
        return bool(self.find_ancestor(other))

    def is_descendant(self, other: "TreeNode") -> bool:
        if other is None:
            return False
        node = self.first_child
        while node is not None and node is not self:
            if node == other:
                return True
            node = node.dfs_next(root_of_search=self)
        return False

    def __lt__(self, other: "TreeNode") -> bool:
        return self.is_ancestor(other)

    def __le__(self, other: "TreeNode") -> bool:
        return self is other or self.is_ancestor(other)

    def __eq__(self, other: "TreeNode") -> bool:
        return self.name == other.name

    def __ne__(self, other: "TreeNode") -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: "TreeNode") -> bool:
        return self.is_descendant(other)

    def __ge__(self, other: "TreeNode") -> bool:
        return self is other or self.is_descendant(other)

    # TODO __repr__
    # TODO __hash__


# ############################################################################
#                                                  VISITOR INTERFACE TRAVERSAL
# ############################################################################


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
                self.buf += str(node.payload)
            self.close_tag(node.name)
        else:
            self.indent()
            self.open_tag(node.name)
        self.buf += "\n"

    def exit_node(self, node: TreeNode):
        self.indent()
        self.close_tag(node.name)
        self.buf += "\n"

    def clear_buffer(self):
        self.buf = ""


def depth_first_traverse(node: TreeNode, visitor: TreeNodeVisitor, indent_level=0):
    """
    Walks the tree (or a branch of the tree) with an object that implements the TreeNodeVisitor interface.
    """
    visitor.tree_depth = indent_level
    visitor.enter_node(node)
    if node.is_leaf():
        return
    child = node.first_child
    while True:
        depth_first_traverse(child, visitor, indent_level + 1)
        child = child.next_sibling
        if child is None:
            break
    visitor.tree_depth = indent_level
    visitor.exit_node(node)


def xml_dump(node: TreeNode) -> str:
    xmlStreamer: XMLTreeNodeVisitor = XMLTreeNodeVisitor()
    depth_first_traverse(node, xmlStreamer)
    return str(xmlStreamer.buf)


# def next_leaf_node(node: TreeNode) -> TreeNode:
#     """
#     Assuming that the given node is a leaf node, determines the next leaf
#     (per a depth-first-search).
#     (Not used?)
#     """
#     result: TreeNode
#     if node.next_sibling:
#         return node.next_sibling.first_leaf_node()
#     elif node.parent:
#         return next_leaf_node(node.parent)
#     return None
