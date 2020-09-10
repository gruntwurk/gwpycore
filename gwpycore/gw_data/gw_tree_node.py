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


__all__ = ("TreeNode",)
