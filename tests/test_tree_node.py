
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
        self.Head.add_child(self.Abe)

        self.Becky = TreeNode("Becky", "Child")
        self.Head.add_child(self.Becky)

        self.Chuck = TreeNode("Chuck", "Child")
        self.Head.add_child(self.Chuck)

        self.David = TreeNode("David", "Child")
        self.Head.add_child(self.David)

        self.Edward = TreeNode("Edward", "Grandchild")
        self.Abe.add_child(self.Edward)

        self.Frank = TreeNode("Frank", "Grandchild")
        self.Abe.add_child(self.Frank)

        self.Gloria = TreeNode("Gloria", "Grandchild")
        self.Chuck.add_child(self.Gloria)

        self.Howard = TreeNode("Howard", "GreatGrandchild")
        self.Edward.add_child(self.Howard)

        self.Irene = TreeNode("Irene", "GreatGrandchild")
        self.Edward.add_child(self.Irene)

        self.Jack = TreeNode("Jack", "GreatGrandchild")
        self.Gloria.add_child(self.Jack)


def test_baseline():
    sample = Sample()
    assert sample.Head.child_count() == 4
    assert sample.Abe.child_count() == 2
    assert sample.Becky.child_count() == 0
    assert sample.Chuck.child_count() == 1
    assert sample.David.child_count() == 0
    assert sample.Edward.child_count() == 2
    assert sample.Frank.child_count() == 0
    assert sample.Gloria.child_count() == 1
    assert sample.Jack.child_count() == 0

    assert repr(sample.Head).startswith("<gwpycore.data.tree_node.TreeNode object at 0x")

    assert str(sample.Head) == '(name="XML", first_child=Abe, last_child=David)'
    assert str(sample.Abe) == '(name="Abe", parent=XML, first_child=Edward, last_child=Frank, next_sibling=Becky)'
    assert str(sample.Becky) == '(name="Becky", parent=XML, next_sibling=Chuck)'
    assert str(sample.Chuck) == '(name="Chuck", parent=XML, first_child=Gloria, last_child=Gloria, next_sibling=David)'
    assert str(sample.David) == '(name="David", parent=XML)'
    assert str(sample.Edward) == '(name="Edward", parent=Abe, first_child=Howard, last_child=Irene, next_sibling=Frank)'
    assert str(sample.Frank) == '(name="Frank", parent=Abe)'
    assert str(sample.Gloria) == '(name="Gloria", parent=Chuck, first_child=Jack, last_child=Jack)'
    assert str(sample.Jack) == '(name="Jack", parent=Gloria)'


def test_clone_assignment():
    node_123 = TreeNode(123)
    assert node_123.name == "123"
    assert node_123.parent is None
    assert node_123.first_child is None
    assert node_123.last_child is None
    assert node_123.next_sibling is None
    assert node_123.payload is None

    node_123_clone = TreeNode(node_123)
    assert node_123 is not node_123_clone
    assert node_123 != node_123_clone
    assert node_123_clone.name == "123"
    assert node_123_clone.parent is None
    assert node_123_clone.first_child is None
    assert node_123_clone.last_child is None
    assert node_123_clone.next_sibling is None
    assert node_123_clone.payload is None

    node_has_payload = TreeNode("has_payload", "a simple payload")
    node_has_payload.parent = node_123
    assert node_has_payload.name == "has_payload"
    assert node_has_payload.parent is node_123
    assert node_has_payload.parent == node_123
    assert node_has_payload.first_child is None
    assert node_has_payload.last_child is None
    assert node_has_payload.next_sibling is None
    assert node_has_payload.payload == "a simple payload"

    node_has_payload_clone = TreeNode(node_has_payload)
    assert node_has_payload is not node_has_payload_clone
    assert node_has_payload != node_has_payload_clone
    assert node_has_payload_clone.name == "has_payload"
    assert node_has_payload_clone.parent is node_123
    assert node_has_payload_clone.parent == node_123
    assert node_has_payload_clone.first_child is None
    assert node_has_payload_clone.last_child is None
    assert node_has_payload_clone.next_sibling is None
    assert node_has_payload_clone.payload == "a simple payload"


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
    sample=Sample()
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
    assert sample.Frank.parent != sample.Abe
    assert sample.Frank.parent.last_child == sample.Frank
    assert sample.Frank.parent.first_child == sample.Frank
    assert sample.Frank.parent.child_count() == 1
