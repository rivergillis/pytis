import unittest
from node import Node


class TestNodes(unittest.TestCase):

    def test_make_node(self):
        n = Node(0, 0)
        self.assertEqual(n.xpos, 0)
        self.assertEqual(n.ypos, 0)
        self.assertEqual(n.pc, 0)
        self.assertEqual(n.acc, 0)
        self.assertEqual(n.bak, 0)
        self.assertTrue(n.is_valid)
        n.lines = ["ADD 1"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        self.assertEqual(n.code, {0: ("ADD", 1, None)})

    def test_add_i_and_pc(self):
        n = Node(0, 0)
        n.lines = ["ADD 1", "ADD 50", "ADD -3"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        self.assertEqual(n.pc, 1)
        self.assertEqual(n.acc, 1)
        n.execute_next()
        self.assertEqual(n.pc, 2)
        self.assertEqual(n.acc, 51)
        n.execute_next()
        self.assertEqual(n.pc, 0)
        self.assertEqual(n.acc, 48)
        n.execute_next()
        self.assertEqual(n.pc, 1)
        self.assertEqual(n.acc, 49)

    def test_sub_i(self):
        n = Node(0, 0)
        n.lines = ["SUB 1", "SUB 50", "SUB -3"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        self.assertEqual(n.acc, -1)
        n.execute_next()
        self.assertEqual(n.acc, -51)
        n.execute_next()
        self.assertEqual(n.acc, -48)

    def test_neg(self):
        n = Node(0, 0)
        n.lines = ["ADD 50", "NEG", "NEG"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        n.execute_next()
        self.assertEqual(n.acc, -50)
        n.execute_next()
        self.assertEqual(n.acc, 50)

    def test_sav_swp(self):
        n = Node(0, 0)
        n.lines = ["ADD 20", "SAV", "ADD 50", "SWP"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        n.execute_next()
        self.assertEqual(n.bak, n.acc)
        self.assertEqual(n.bak, 20)
        n.execute_next()
        self.assertNotEqual(n.bak, n.acc)
        self.assertEqual(n.bak, 20)
        n.execute_next()
        self.assertEqual(n.bak, n.acc)
        self.assertEqual(n.bak, 20)


if __name__ == '__main__':
    unittest.main()
