
from gwpycore import TreeNode, XMLTreeNodeVisitor, add_child, add_new_child, add_sibling, depth_first_traverse, insert_parent, insert_sibling, simplify_parentage, split_tree


class Sample():
    """
    *                     Head
    *                       |
    *           +-------+---+---+-------+
    *           |       |       |       |
    *          Abe    Becky   Chuck   David
    *           |               |
    *       +---+---+           |
    *       |       |           |
    *     Edward  Frank      Gloria
    *       |                   |
    *    +--+--+                |
    *    |     |                |
    * Howard Irene            Jack
    """

    def __init__(self) -> None:
        self.nodeHead = TreeNode("XML", "")
        self.nodeAbe = add_new_child(self.nodeHead, "Abe", "Child")
        self.nodeBecky = add_new_child(self.nodeHead, "Becky", "Child")
        self.nodeChuck = add_new_child(self.nodeHead, "Chuck", "Child")
        self.nodeDavid = add_new_child(self.nodeHead, "David", "Child")
        self.nodeEdward = add_new_child(self.nodeAbe, "Edward", "Grandchild")
        self.nodeFrank = add_new_child(self.nodeAbe, "Frank", "Grandchild")
        self.nodeGloria = add_new_child(self.nodeChuck, "Gloria", "Grandchild")
        self.nodeHoward = add_new_child(self.nodeEdward, "Howard", "GreatGrandchild")
        self.nodeIrene = add_new_child(self.nodeEdward, "Irene", "GreatGrandchild")
        self.nodeJack = add_new_child(self.nodeGloria, "Jack", "GreatGrandchild")


def test_baseline():
    sample = Sample()
    # Just test the nodes added in Setup
    assert sample.nodeHead.child_count() == 4
    assert sample.nodeAbe.child_count() == 2
    assert sample.nodeBecky.child_count() == 0
    assert sample.nodeChuck.child_count() == 1
    assert sample.nodeDavid.child_count() == 0
    assert sample.nodeEdward.child_count() == 2
    assert sample.nodeFrank.child_count() == 0
    assert sample.nodeGloria.child_count() == 1
    assert sample.nodeJack.child_count() == 0


def test_insert_parent():
    """
    * Test for InsertParent...
    *
    *                            Head
    *                              |
    *                  +-------+---+---+-------+
    *                  |       |       |       |
    *                 Abe    Becky   Chuck   David
    *                  |               |
    *              +---+---+           | <-- Insert "Nancy"
    *              |       |           |
    *            Edward  Frank       Gloria
    *              |                   |
    *           +--+--+                |
    *           |     |                |
    *        Howard Irene            Jack
    """
    sample = Sample()
    nodeNancy: TreeNode = TreeNode("Nancy", "StepMother")
    insert_parent(sample.nodeGloria, nodeNancy)
    assert sample.nodeGloria.parent == nodeNancy
    assert nodeNancy.parent == sample.nodeChuck
    assert sample.nodeChuck.first_child == nodeNancy
    assert sample.nodeChuck.last_child == nodeNancy
    assert sample.nodeChuck.child_count() == 1


def test_simplify_parentage():
    """
    *   Test for SimplifyParentage...
    *
    *                             Head
    *                               |
    *                   +-------+---+---+-------+
    *                   |       |       |       |
    *                  Abe    Becky     |     David
    *                   |               |
    *               +---+---+           | <-- Chuck, Nancy, & Gloria removed
    *               |       |           |
    *             Edward  Frank         |
    *               |                   |
    *            +--+--+                |
    *            |     |                |
    *         Howard Irene            Jack
    """
    sample = Sample()
    nodeNancy: TreeNode = TreeNode("Nancy", "StepMother")
    insert_parent(sample.nodeGloria, nodeNancy)
    simplify_parentage(sample.nodeJack)
    assert sample.nodeJack.parent == sample.nodeHead
    assert sample.nodeBecky.next_sibling == sample.nodeJack
    assert sample.nodeDavid.previous_sibling() == sample.nodeJack
    assert sample.nodeHead.child_count() == 4


def test_add_various():
    """
    *                          Head
    *                            |
    *                +-------+---+---+-------+
    *                |       |       |       |
    *              Abe    Becky   Chuck   David
    *                |               |
    *            +---+---+           |
    *            |       |           |
    *          Edward  Frank       Gloria
    *            |                   |
    *        +--+--+                +-----+-------+------+
    *        |     |                |     |       |      |
    *      Howard Irene            Jack (Kathy) (Larry) (Mary)
    """
    sample = Sample()
    nodeLarry: TreeNode = TreeNode("Larry", "StepChild")
    add_sibling(sample.nodeJack, nodeLarry)
    assert nodeLarry == sample.nodeGloria.last_child
    assert sample.nodeGloria.child_count() == 2
    nodeMary: TreeNode = TreeNode("Mary", "StepChild")
    add_child(sample.nodeGloria, nodeMary)
    assert nodeMary == sample.nodeGloria.last_child
    assert sample.nodeGloria.child_count() == 3
    nodeKathy: TreeNode = TreeNode("Kathy", "StepChild")
    insert_sibling(nodeLarry, nodeKathy)
    assert nodeKathy == sample.nodeJack.next_sibling
    assert sample.nodeGloria.child_count() == 4


def test_XMLTreeNodeVisitor():
    sample = Sample()
    xmlStreamer: XMLTreeNodeVisitor = XMLTreeNodeVisitor()
    depth_first_traverse(sample.nodeHead, xmlStreamer)
    # print (xmlStreamer.buf)
    assert xmlStreamer.buf == """<XML>
  <Abe>
    <Edward>
      <Howard>GreatGrandchild</Howard>
      <Irene>GreatGrandchild</Irene>
    </Edward>
    <Frank>Grandchild</Frank>
  </Abe>
  <Becky>Child</Becky>
  <Chuck>
    <Gloria>
      <Jack>GreatGrandchild</Jack>
    </Gloria>
  </Chuck>
  <David>Child</David>
</XML>
"""
    xmlStreamer.clear_buffer()
    depth_first_traverse(sample.nodeEdward, xmlStreamer)
    # print (xmlStreamer.buf)
    assert xmlStreamer.buf == """<Edward>
  <Howard>GreatGrandchild</Howard>
  <Irene>GreatGrandchild</Irene>
</Edward>
"""


def test_split_tree():
    """
    *                               Head
    *                                 |
    *                     +-------+---+---+-------+
    *                     |       |       |       |
    *                    Abe    Becky   Chuck   David
    *                     |               |
    *                 +---+---+           |
    *                 |       |           |
    *               Edward  Frank       Gloria
    *                 |                   |
    *              +--+--+     \\           |
    *              |     |      \\          |
    *           Howard Irene     \\       Jack
    *                             \\
    *                              Split the Abe tree so that Frank gets a second Abe parent all to itself
    """
    sample = Sample()
    assert sample.nodeEdward.parent == sample.nodeAbe
    assert sample.nodeFrank.parent == sample.nodeAbe
    assert sample.nodeFrank.parent.first_child == sample.nodeEdward
    assert sample.nodeFrank.parent.last_child == sample.nodeFrank
    split_tree(sample.nodeFrank)
    assert sample.nodeEdward.parent != sample.nodeAbe
    assert sample.nodeFrank.parent == sample.nodeAbe
    assert sample.nodeFrank.parent.last_child == sample.nodeFrank
    assert sample.nodeFrank.parent.first_child == sample.nodeFrank
    assert sample.nodeFrank.parent.child_count() == 1
