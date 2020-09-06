class Node():
    """
    A generic tree node.
    Compatible with Qt Tree Model/View (in conjuction with QModel Index).
    Possibly useful in other contexts, as well.

    name -- a (display) name for the node.
    payload -- any object associated with the node.
    parent -- this node's parent node (or None if this is the root node).
    """
    def __init__(self, name:str, parent, payload:any=None):
        self.name = name
        self.payload = payload
        self.tool_tip = name
        self.parent = parent
        self.children = []

    def position(self):
        """
        Which child am I? (0 = the eldest)
        """
        position = 0
        if self.parent:
            for child in self.parent.children:
                if child == self:
                    break
                position += 1
        return position

    def sibling(self):
        """
        Who is my next younger sibling? (or None)
        """
        sib = None
        me = self.position()
        if self.parent:
            if len(self.parent.children) > me+1:
                sib = self.parent.children[me+1]
        return sib

    def dfs_next(self):
        """
        Who is the next node in Depth-First-Search order?
        """
        next = None
        if self.children:
            next = self.children[0]
        elif self.sibling():
            next = self.sibling()
        elif self.parent:
            next = self.parent.sibling()
        return next

__all__ = ("Node",)