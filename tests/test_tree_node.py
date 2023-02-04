
from gwpycore import TreeNode, XMLTreeNodeVisitor, depth_first_traverse


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
        self.Head = TreeNode("XML", "")
        self.Abe = TreeNode("Abe", "Child")
        self.Becky = TreeNode("Becky", "Child")
        self.Chuck = TreeNode("Chuck", "Child")
        self.David = TreeNode("David", "Child")
        self.Edward = TreeNode("Edward", "Grandchild")
        self.Frank = TreeNode("Frank", "Grandchild")
        self.Gloria = TreeNode("Gloria", "Grandchild")
        self.Howard = TreeNode("Howard", "GreatGrandchild")
        self.Irene = TreeNode("Irene", "GreatGrandchild")
        self.Jack = TreeNode("Jack", "GreatGrandchild")
        self.Head.add_child(self.Abe)
        self.Head.add_child(self.Becky)
        self.Head.add_child(self.Chuck)
        self.Head.add_child(self.David)
        self.Abe.add_child(self.Edward)
        self.Abe.add_child(self.Frank)
        self.Chuck.add_child(self.Gloria)
        self.Edward.add_child(self.Howard)
        self.Edward.add_child(self.Irene)
        self.Gloria.add_child(self.Jack)


def test_baseline():
    sample = Sample()
    # Just test the s added in Setup
    assert sample.Head.child_count() == 4
    assert sample.Abe.child_count() == 2
    assert sample.Becky.child_count() == 0
    assert sample.Chuck.child_count() == 1
    assert sample.David.child_count() == 0
    assert sample.Edward.child_count() == 2
    assert sample.Frank.child_count() == 0
    assert sample.Gloria.child_count() == 1
    assert sample.Jack.child_count() == 0


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
    Nancy = TreeNode("Nancy", "StepMother")
    sample.Gloria.insert_parent(Nancy)
    assert sample.Gloria.parent == Nancy
    assert Nancy.parent == sample.Chuck
    assert sample.Chuck.first_child == Nancy
    assert sample.Chuck.last_child == Nancy
    assert sample.Chuck.child_count() == 1


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
    Nancy = TreeNode("Nancy", "StepMother")
    sample.Gloria.insert_parent(Nancy)
    sample.Jack.simplify_parentage()
    assert sample.Jack.parent == sample.Head
    assert sample.Becky.next_sibling == sample.Jack
    assert sample.David.previous_sibling() == sample.Jack
    assert sample.Head.child_count() == 4


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
    Larry: TreeNode = TreeNode("Larry", "StepChild")
    sample.Jack.add_sibling(Larry)
    assert Larry == sample.Gloria.last_child
    assert sample.Gloria.child_count() == 2
    Mary: TreeNode = TreeNode("Mary", "StepChild")
    sample.Gloria.add_child(Mary)
    assert Mary == sample.Gloria.last_child
    assert sample.Gloria.child_count() == 3
    Kathy: TreeNode = TreeNode("Kathy", "StepChild")
    Larry.insert_sibling(Kathy)
    assert Kathy == sample.Jack.next_sibling
    assert sample.Gloria.child_count() == 4


def test_XMLTreeVisitor():
    sample = Sample()
    xmlStreamer: XMLTreeNodeVisitor = XMLTreeNodeVisitor()
    depth_first_traverse(sample.Head, xmlStreamer)
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
    depth_first_traverse(sample.Edward, xmlStreamer)
    # print (xmlStreamer.buf)
    assert xmlStreamer.buf == """<Edward>
  <Howard>GreatGrandchild</Howard>
  <Irene>GreatGrandchild</Irene>
</Edward>
"""


def test_split_branch():
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
    assert sample.Edward.parent == sample.Abe
    assert sample.Frank.parent == sample.Abe
    assert sample.Frank.parent.first_child == sample.Edward
    assert sample.Frank.parent.last_child == sample.Frank
    sample.Frank.split_branch()
    assert sample.Edward.parent is sample.Abe
    assert sample.Edward.parent == sample.Abe
    assert sample.Frank.parent is not sample.Abe
    assert sample.Frank.parent == sample.Abe
    assert sample.Frank.parent.last_child == sample.Frank
    assert sample.Frank.parent.first_child == sample.Frank
    assert sample.Frank.parent.child_count() == 1
