from abc import ABC, abstractmethod

class TreeNode:
    """
    A node in a classic tree structure where any node can have zero
    or more children.

    name -- a (display) name for the node.
    payload -- any object associated with the node.
    copy_from -- if provided, this node will become a clone of that one.

    If you descend from this class, be sure to reimplement the assign() method
    and have it copy the data appropriately. Also, the factoryCreate() method
    must be overloaded to create the proper descendat class.
    """

    def __init__(
        self, name: str = "", payload: any = None, copy_from: "TreeNode" = None
    ):
        self.name: str = name
        self.payload: any = payload
        self.parent: "TreeNode" = None
        self.first_child: "TreeNode" = None
        self.last_child: "TreeNode" = None
        self.next_sibling: "TreeNode" = None
        if copy_from:
            self.parent = copy_from.parent
            self.first_child = copy_from.first_child
            self.last_child = copy_from.last_child
            self.next_sibling = copy_from.next_sibling
            if not self.name:
                self.name = copy_from.name
            if not self.payload:
                self.payload = copy_from.payload

    def __str__(self) -> str:
        name = "" if not self.name else self.name
        parent_name = "" if not self.parent else self.parent.name
        first_child_name = "" if not self.first_child else self.first_child.name
        last_child_name = "" if not self.last_child else self.last_child.name
        next_sibling_name = "" if not self.next_sibling else self.next_sibling.name
        return f"(name = {name}, parent = {parent_name}, first_child = {first_child_name}, last_child = {last_child_name}, next_sibling = {next_sibling_name})"

    def is_leaf(self) -> bool:
        """
        Whether or not self is a leaf node (i.e. True if the node has no children).
        """
        return self.first_child == None

    def child_count(self) -> int:
        """
        The number of children that belong to this node.
        """
        child = self.first_child
        result = 0
        while child != None:
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
        if self.parent == None:
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
        for i in range(position + 1):
            if result:
                result = result.next_sibling
            else:
                break
        return result


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


def add_child(existing_node: TreeNode, new_node: TreeNode):
    """
    Adds the given new node into the tree as a child of the referenced node
    (becoming the  "last child").
    """
    new_node.parent = existing_node
    if existing_node.is_leaf():
        existing_node.first_child = new_node
    else:
        existing_node.last_child.next_sibling = new_node
    existing_node.last_child = new_node


def add_new_child(existing_node: TreeNode, name: str, payload: any) -> TreeNode:
    child = TreeNode(name, payload)
    add_child(existing_node, child)
    return child


def add_sibling(existing_node: TreeNode, new_node: TreeNode):
    """
    Adds the given new node into the tree as the immediate next sibling of
    the existing node.
    """
    if existing_node.parent:
        add_child(existing_node.parent, new_node)


def insert_sibling(existing_node: TreeNode, new_node: TreeNode):
    """
    Inserts the given new node into the tree as the immediate prior sibling
    of the referenced node.
    """
    prev_sib: TreeNode = existing_node.previous_sibling()
    new_node.parent = existing_node.parent
    new_node.next_sibling = existing_node
    if prev_sib:
        prev_sib.next_sibling = new_node
    else:
        existing_node.parent.first_child = new_node


def insert_parent(existing_node: TreeNode, new_node: TreeNode):
    """
    Inserts the given new node into the tree in place of the referenced
    node, with the referenced node becoming a child of the new node.
    """
    # First, insert the node as a sibling, then move "self" to be a child (the only child) of it.
    insert_sibling(existing_node, new_node)
    new_node.next_sibling = existing_node.next_sibling
    if new_node.next_sibling == None:
        new_node.parent.last_child = new_node
    existing_node.next_sibling = None
    new_node.first_child = existing_node
    new_node.last_child = existing_node
    existing_node.parent = new_node


def remove_parent(node: TreeNode):
    """
    Promote self node, along with any and all siblings to the level of its
    parent, replacing the parent.
    """
    originalParent: TreeNode = node.parent
    grandParent: TreeNode = originalParent.parent

    # Change this node and all of its siblings to claim the grandparent as their  parent.
    childNode: TreeNode = originalParent.first_child
    while childNode != None:
        childNode.parent = grandParent
        childNode = childNode.next_sibling

    # Link the first grandchild to the original parent's previous sibling
    if grandParent:
        if grandParent.first_child == originalParent:
            grandParent.first_child = originalParent.first_child
        else:
            originalParent.previous_sibling().next_sibling = originalParent.first_child

    # Link the last grandchild to the original parent's next sibling
    if originalParent.next_sibling:
        originalParent.last_child.next_sibling = originalParent.next_sibling
    elif grandParent:
        grandParent.last_child = originalParent.last_child
    # Clear the original parent's references to its children.
    originalParent.last_child = None
    originalParent.first_child = None


def simplify_parentage(node: TreeNode):
    """
    If this node is an only child, it will be promoted to take over for its
    parent. If that makes it the only child of the grandparent, it is
    promoted again, ad infinitum.
    """
    while node.is_only_child():
        remove_parent(node)


def split_tree(node: TreeNode):
    """
    Split the tree between the given node and its previous sibling(s).
    All of the previous siblings are moved to their own branch
    with a new parent, leaving this node and any siblings on the right
    with the original parent.
    """

    # If this is the first node of a subtree, there is nothing to split.
    if node.parent.first_child == node:
        return
    parent_clone = TreeNode(copy_from=node.parent)
    insert_sibling(node.parent, parent_clone)
    node.parent.first_child = node
    older_sibling = parent_clone.first_child
    while older_sibling != node:
        older_sibling.parent = parent_clone
        older_sibling = older_sibling.next_sibling
    older_sibling.next_sibling = None
    parent_clone.last_child = older_sibling


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
        if child == None:
            break
    visitor.tree_depth = indent_level
    visitor.exit_node(node)


def xml_dump(node: TreeNode):
    xmlStreamer: XMLTreeNodeVisitor = XMLTreeNodeVisitor()
    depth_first_traverse(node, xmlStreamer)
    print(xmlStreamer.buf)


def dfs_next(node: TreeNode):
    """
    Who is the next node in Depth-First-Search order?
    """
    next = None
    if node.first_child:
        next = node.first_child
    elif node.next_sibling:
        next = node.next_sibling
    elif node.parent:
        next = node.parent.next_sibling
    return next


def next_leaf_node(node: TreeNode) -> TreeNode:
    """
    Assuming that the given node is a leaf node, determines the next leaf
    (per a depth-first-search).
    (Not used?)
    """
    result: TreeNode
    if node.next_sibling:
        return node.next_sibling.first_leaf_node()
    elif node.parent:
        return next_leaf_node(node.parent)
    return None


__all__ = ["TreeNode", "TreeNodeVisitor", "XMLTreeNodeVisitor",
"add_child",
    "add_new_child",
    "add_sibling",
    "depth_first_traverse",
    "dfs_next",
    "insert_parent",
    "insert_sibling",
    "next_leaf_node",
    "remove_parent",
    "simplify_parentage",
    "split_tree",
    "xml_dump"
]
