import unittest
from node import Node
import main


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

    def test_mov_no_delay(self):
        n1 = Node(0, 0)  # upper node
        n2 = Node(0, 1)  # lower node
        n1.full_debug = True
        n2.full_debug = True
        nodes = [n1, n2]
        main.build_io_tables(nodes)

        n1.lines = ["MOV 2, DOWN", "NOP"]
        n2.lines = ["MOV UP, ACC", "NOP"]
        n1.parse_lines()
        n2.parse_lines()

        self.assertTrue(n1.is_valid)
        self.assertTrue(n2.is_valid)

        n1.execute_next()
        self.assertIsNone(n1.receiving)  # n1 is not receiving
        self.assertFalse(n1.receiving_into_acc)  # n1 is not receiving into acc
        self.assertEqual(n1.sending, n2)  # n1 is sending to n2
        self.assertEqual(n1.value_to_send, 2)  # n1 is sending the value 2
        self.assertEqual(n1.acc, 0)
        self.assertEqual(n1.pc, 0)  # pc not increased yet

        # n2 has yet to do anything
        self.assertIsNone(n2.receiving)
        self.assertIsNone(n2.sending)
        self.assertIsNone(n2.value_to_send)
        self.assertFalse(n2.receiving_into_acc)
        self.assertEqual(n2.acc, 0)
        self.assertEqual(n2.pc, 0)

        n2.execute_next()
        self.assertIsNone(n2.receiving)  # n2 has fully received
        self.assertFalse(n2.receiving_into_acc)
        self.assertIsNone(n2.sending)
        self.assertIsNone(n2.value_to_send)
        self.assertEqual(n2.acc, 2)  # n2 has received 2 into its acc
        self.assertEqual(n2.pc, 1)  # n2 has left the mov statement

        # n1 has clean IO
        self.assertIsNone(n1.receiving)
        self.assertFalse(n1.receiving_into_acc)
        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)
        self.assertEqual(n1.acc, 0)
        self.assertEqual(n1.pc, 1)

        # no weird future effects, both have clean IO
        n1.execute_next()
        n2.execute_next()
        self.assertEqual(n1.acc, 0)
        self.assertEqual(n2.acc, 2)
        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.receiving)
        self.assertIsNone(n1.value_to_send)
        self.assertFalse(n1.receiving_into_acc)
        self.assertIsNone(n2.sending)
        self.assertIsNone(n2.receiving)
        self.assertIsNone(n2.value_to_send)
        self.assertFalse(n2.receiving_into_acc)
        self.assertEqual(n1.pc, 0)
        self.assertEqual(n2.pc, 0)


if __name__ == '__main__':
    unittest.main()
