from gwpycore.gw_data.gw_tree_node_visitor import TreeNodeVisitor
from gwpycore.gw_data.gw_tree_node import TreeNode

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


def add_new_child(existing_node: TreeNode,name:str, payload:any) -> TreeNode:
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
    prevSib: TreeNode = existing_node.previous_sibling()
    new_node.parent = existing_node.parent
    new_node.next_sibling = existing_node
    if (prevSib != None):
       prevSib.next_sibling = new_node
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
    if (new_node.next_sibling == None):
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
    originalParent: TreeNode=node.parent
    grandParent: TreeNode=originalParent.parent

    # Change this node and all of its siblings to claim the grandparent as their  parent.
    childNode: TreeNode=originalParent.first_child
    while childNode != None:
        childNode.parent=grandParent
        childNode=childNode.next_sibling

    # Link the first grandchild to the original parent's previous sibling
    if (grandParent):
        if (grandParent.first_child == originalParent):
           grandParent.first_child=originalParent.first_child
        else:
            originalParent.previous_sibling().next_sibling=originalParent.first_child

    # Link the last grandchild to the original parent's next sibling
    if (originalParent.next_sibling):
        originalParent.last_child.next_sibling=originalParent.next_sibling
    elif (grandParent):
        grandParent.last_child=originalParent.last_child
    # Clear the original parent's references to its children.
    originalParent.last_child=None
    originalParent.first_child=None

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
    if (node.parent.first_child == node):
       return
    parent_clone=TreeNode(copy_from = node.parent)
    insert_sibling(node.parent, parent_clone)
    node.parent.first_child=node
    older_sibling=parent_clone.first_child
    while older_sibling != node:
        older_sibling.parent=parent_clone
        older_sibling=older_sibling.next_sibling
    older_sibling.next_sibling=None
    parent_clone.last_child=older_sibling

def depth_first_traverse(node: TreeNode, visitor: TreeNodeVisitor, indent_level = 0):
    """
    Walks the tree (or a branch of the tree) with an object that implements the TreeNodeVisitor interface.
    """
    visitor.tree_depth = indent_level
    visitor.enter_node(node)
    if node.is_leaf():
       return
    child=node.first_child
    while True:
        depth_first_traverse(child, visitor, indent_level + 1)
        child=child.next_sibling
        if (child == None):
           break
    visitor.tree_depth = indent_level
    visitor.exit_node(node)


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
    if (node.next_sibling):
        return node.next_sibling.first_leaf_node()
    elif (node.parent):
        return next_leaf_node(node.parent)
    return None
