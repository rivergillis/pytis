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

    def test_labels_full_line(self):
        n = Node(0, 0)
        n.lines = ["ADD 5", "label:", "SUB 20", "labeltwo:"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        n.execute_next()
        self.assertEqual(n.pc, 2)
        self.assertEqual(n.acc, 5)
        n.execute_next()
        self.assertEqual(n.pc, 3)
        n.execute_next()
        self.assertEqual(n.pc, 0)
        self.assertEqual(n.acc, -15)

    def test_jmp(self):
        n = Node(0, 0)
        n.lines = ["ADD 5", "label:", "SUB 20",
                   "labeltwo:", "JMP label", "ADD 20"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        for i in range(4):
            n.execute_next()
        self.assertEqual(n.pc, 4)
        self.assertEqual(n.acc, -15)
        n.execute_next()
        self.assertEqual(n.pc, 1)
        n.execute_next()
        n.execute_next()  # execute SUB 20
        self.assertEqual(n.pc, 3)
        self.assertEqual(n.acc, -35)
        for i in range(400):
            n.execute_next()
        self.assertEqual(n.pc, 3)
        self.assertEqual(n.acc, -2035)

    def test_jez_jnz(self):
        n = Node(0, 0)
        n.lines = ["JNZ label", "JEZ label", "ADD 1",
                   "label:", "ADD 5", "JEZ label", "JNZ label"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        n.execute_next()
        self.assertEqual(n.pc, 3)
        self.assertEqual(n.acc, 0)
        for i in range(4):
            n.execute_next()
        self.assertEqual(n.pc, 3)
        self.assertNotEqual(n.acc, 0)

    def test_jgz_jlz(self):
        n = Node(0, 0)
        n.lines = ["JGZ label", "JLZ label", "ADD 20", "label:", "NEG"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        for i in range(6):  # execute JGZ when acc=-20
            n.execute_next()
        self.assertEqual(n.pc, 1)
        self.assertLess(n.acc, 0)
        n.execute_next()
        self.assertEqual(n.pc, 3)
        for i in range(3):
            n.execute_next()  # execute JGZ when acc=20
        self.assertEqual(n.pc, 3)
        self.assertGreater(n.acc, 0)

    def test_nop(self):
        n = Node(0, 0)
        n.lines = ["ADD 20", "NOP", "NOP", "ADD 20"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        for i in range(4):
            n.execute_next()
        self.assertEqual(n.acc, 40)
        self.assertEqual(n.pc, 0)

    def test_jro(self):
        n = Node(0, 0)
        n.lines = ["ADD 2", "JRO ACC", "NOP",
                   "JRO -3", "NOP", "JRO -5", "NOP", "SUB 6"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        n.execute_next()
        n.execute_next()
        self.assertEqual(n.acc, 2)
        self.assertEqual(n.pc, 3)
        for i in range(3):
            n.execute_next()
        self.assertEqual(n.acc, 4)
        self.assertEqual(n.pc, 5)
        for i in range(3):
            n.execute_next()
        self.assertEqual(n.acc, 6)
        self.assertEqual(n.pc, 7)

    def test_send_receive(self):
        n1 = Node(0, 0)
        n2 = Node(0, 1)

        n1.value_to_send = 52
        n1.sending = n2
        n2.receiving = n1
        n2.receiving_into_acc = True

        self.assertEqual(n2.acc, 0)
        n2.receive_value()

        self.assertEqual(n2.acc, 52)

        self.assertIsNone(n1.value_to_send)
        self.assertIsNone(n1.sending)
        self.assertIsNone(n2.receiving)
        self.assertFalse(n2.receiving_into_acc)


if __name__ == '__main__':
    unittest.main()
