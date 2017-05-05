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

    def test_build_io_tables(self):
        n1 = Node(0, 0)  # upper left node
        n2 = Node(0, 1)  # lower left node
        n3 = Node(1, 0)  # upper right node
        n4 = Node(1, 1)  # lower right node
        nodes = [n1, n2, n3, n4]
        main.build_io_tables(nodes)

        self.assertIsNone(n1.adjacency["LEFT"])
        self.assertEqual(n1.adjacency["DOWN"], n2)
        self.assertEqual(n1.adjacency["RIGHT"], n3)
        self.assertIsNone(n1.adjacency["UP"])

        self.assertIsNone(n2.adjacency["LEFT"])
        self.assertIsNone(n2.adjacency["DOWN"])
        self.assertEqual(n2.adjacency["RIGHT"], n4)
        self.assertEqual(n2.adjacency["UP"], n1)

        self.assertEqual(n3.adjacency["LEFT"], n1)
        self.assertEqual(n3.adjacency["DOWN"], n4)
        self.assertIsNone(n3.adjacency["RIGHT"])
        self.assertIsNone(n3.adjacency["UP"])

        self.assertEqual(n4.adjacency["LEFT"], n2)
        self.assertIsNone(n4.adjacency["DOWN"])
        self.assertIsNone(n4.adjacency["RIGHT"])
        self.assertEqual(n4.adjacency["UP"], n3)

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

    def test_labels_full_line_tis_accurate(self):
        n = Node(0, 0)
        n.lines = ["ADD 5", "label:", "SUB 20", "labeltwo:"]
        n.parse_lines()
        self.assertTrue(n.is_valid)

        n.execute_next()
        # adds 5, pc now points to sub 20
        self.assertEqual(n.acc, 5)
        self.assertEqual(n.pc, 2)

        n.execute_next()
        # subs 20, pc now points to add 5
        self.assertEqual(n.acc, -15)
        self.assertEqual(n.pc, 0)

        n.execute_next()
        # adds 5, pc now points to sub 20
        self.assertEqual(n.acc, -10)
        self.assertEqual(n.pc, 2)

    def test_jmp_tis_accurate(self):
        n = Node(0, 0)
        n.lines = ["ADD 5", "label:", "SUB 20",
                   "labeltwo:", "JMP label", "ADD 20"]
        n.parse_lines()
        self.assertTrue(n.is_valid)

        # frame 1:
        n.execute_next()
        # n has added 5 and the pc now points to sub 20
        self.assertEqual(n.acc, 5)
        self.assertEqual(n.pc, 2)

        # frame 2:
        n.execute_next()
        # n has subbed 20 and the pc now points to jmp label
        self.assertEqual(n.acc, -15)
        self.assertEqual(n.pc, 4)

        # frame 3:
        n.execute_next()
        # n has jumped and the pc now points to sub 20
        self.assertEqual(n.acc, -15)
        self.assertEqual(n.pc, 2)

        # frame 4:
        n.execute_next()
        # n has subbed 20 and the pc now points to jmp label
        self.assertEqual(n.acc, -35)
        self.assertEqual(n.pc, 4)

    def test_jez_jnz_tis_accurate(self):
        n = Node(0, 0)
        n.lines = ["JNZ label", "JEZ label", "ADD 1",
                   "label:", "ADD 5", "JEZ label", "JNZ label"]
        n.parse_lines()
        self.assertTrue(n.is_valid)

        n.execute_next()
        n.execute_next()
        self.assertEqual(n.pc, 4)
        self.assertEqual(n.acc, 0)

        for i in range(3):
            n.execute_next()
        self.assertEqual(n.pc, 4)
        self.assertEqual(n.acc, 5)

    def test_jgz_jlz_tis_accurate(self):
        n = Node(0, 0)
        n.lines = ["JGZ label", "JLZ label", "ADD 20", "label:", "NEG"]
        n.parse_lines()
        self.assertTrue(n.is_valid)

        for i in range(4):
            n.execute_next()
        self.assertEqual(n.pc, 0)
        self.assertLess(n.acc, 0)

        n.execute_next()
        self.assertEqual(n.pc, 1)

        n.execute_next()
        self.assertEqual(n.pc, 4)

        n.execute_next()
        self.assertEqual(n.pc, 0)
        self.assertGreater(n.acc, 0)

        n.execute_next()
        self.assertEqual(n.pc, 4)

    def test_nop(self):
        n = Node(0, 0)
        n.lines = ["ADD 20", "NOP", "NOP", "ADD 20"]
        n.parse_lines()
        self.assertTrue(n.is_valid)
        for i in range(4):
            n.execute_next()
        self.assertEqual(n.acc, 40)
        self.assertEqual(n.pc, 0)

    def test_jro_tis_accurate(self):
        n = Node(0, 0)
        n.lines = ["ADD 2", "LABEL:", "JRO ACC", "NOP",
                   "LABEL2:", "JRO -3", "NEG", "JRO ACC"]
        n.parse_lines()
        self.assertTrue(n.is_valid)

        n.execute_next()
        self.assertEqual(n.pc, 2)
        self.assertEqual(n.acc, 2)

        n.execute_next()
        # n jumps over the next (2-1=1) lines of code (LABEL: is not a LOC) to
        # JRO
        self.assertEqual(n.pc, 5)
        self.assertEqual(n.acc, 2)

        n.execute_next()
        # n jumps back over (3-1=2) lines of code to ADD 2
        self.assertEqual(n.pc, 0)
        self.assertEqual(n.acc, 2)

        n.execute_next()
        # n adds 2 and skips over the next label
        self.assertEqual(n.pc, 2)
        self.assertEqual(n.acc, 4)

        n.execute_next()
        # n jumps over (4-1=3) LOC to JRO ACC
        self.assertEqual(n.pc, 7)
        self.assertEqual(n.acc, 4)

        n.execute_next()
        # n cannot jump another further! infinite loop
        self.assertEqual(n.pc, 7)
        self.assertEqual(n.acc, 4)

    def test_jro_negbounds_zero(self):
        n = Node(0, 0)
        n0 = Node(0, 1)
        n.lines = ["NOP", "JRO -3", "NOP"]
        n0.lines = ["NOP", "JRO 0", "NOP"]
        n.parse_lines()
        n0.parse_lines()
        self.assertTrue(n.is_valid)
        self.assertTrue(n0.is_valid)

        n.execute_next()
        n0.execute_next()

        n.execute_next()
        # n tries to jump below bounds, gets to NOP
        self.assertEqual(n.pc, 0)

        n0.execute_next()
        # n0 tried to jump over 0 instructs, lands back on JRO
        self.assertEqual(n0.pc, 1)
    
    def test_jro_labels_bounds(self):
        # note: in reality jro should jump to itself when it cannot find a spot
        # but I don't think this matters much, infinite loop either way
        n = Node(0,0)
        n.lines = ["label:", "label2:", "JRO -1", "NOP"]
        n0 = Node(0,1)
        n0.lines = ["JRO 1", "label:", "label2:"]

        n.parse_lines()
        self.assertTrue(n.is_valid)

        n.execute_next()
        #n moves up to the jro
        self.assertEqual(n.pc, 2)

        n.execute_next()
        #n tries to move under the label and cannot
        self.assertEqual(n.pc, 0)

        n0.parse_lines()
        self.assertTrue(n0.is_valid)

        n0.execute_next()
        #n0 tries to move beyond the label and cannot
        self.assertEqual(n0.pc, 2)

    def test_send_receive(self):
        # note: this test is no longer accurate?
        
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
        

    """
    def test_mov_tis_accurate(self):
        # this test is based off a TIS-100 run, this is the only accurate test
        # for IO
        # upon mov completion, the pc of both nodes increase in tandem
        n1 = Node(0, 0)  # upper left node
        n2 = Node(0, 1)  # lower left node
        n3 = Node(1, 0)  # upper right node
        n4 = Node(1, 1)  # lower right node
        nodes = [n1, n2, n3, n4]
        main.build_io_tables(nodes)

        n1.lines = ["ADD 4", "MOV ACC, DOWN", "MOV RIGHT, ACC"]
        n2.lines = ["MOV UP, ACC", "ADD 32",
                    "JMP label", "label:", "MOV ACC, RIGHT"]
        n4.lines = ["MOV LEFT, UP", "NOP"]
        n3.lines = ["MOV DOWN, LEFT", "NOP"]

        # after 1 frame:
        # n1.acc = 4
        # rest waiting
        for n in nodes:
            n.parse_lines()
            self.assertTrue(n.is_valid)
            n.execute_next()

        # idea: have an end_frame() func in each node that sets the
        # value_to_send, called after every node has execute_next()'d
        self.assertEqual(n1.acc, 4)
        self.assertIsNone(n1.sending)  # n1 not sending anything

        self.assertEqual(n2.receiving, n1)  # n2 trying to receive from n1
        self.assertTrue(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        # after 2 frames:
        # n1 is sending 4 to n2
        # n1 pc is still pointing to mov, has yet to increase
        # n2 has yet to pick up 4 from n1
        # rest waiting
        for n in nodes:
            n.execute_next()

        self.assertEqual(n1.sending, n2)
        self.assertEqual(n1.value_to_send, n1.acc)  # n1 sending 4 to n2
        self.assertEqual(n1.pc, 1)  # n1 still on mov statement

        self.assertEqual(n2.acc, 0)  # n2 yet to pick up 4 from n1
        self.assertEqual(n2.pc, 0)  # n2 still on mov statement
        self.assertEqual(n2.receiving, n1)  # n2 trying to receive from n1
        self.assertTrue(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        # after 3 frames:
        # n1 has moved pc down to next mov BUT ONLY POINTS TO IT
        # n2 has picked up 4 from n1 and pc points to add 32
        # n2.acc = 4
        # rest waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertIsNone(n1.receiving)  # n1 not yet trying to receive from n4
        self.assertFalse(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 points to next mov
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 4)  # n2 picked up 4 from n1
        self.assertEqual(n2.pc, 1)  # n2 moved past mov
        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertIsNone(n2.value_to_send)  # with nothing

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        # after 4 frames:
        # n2 has added, pc points to jmp, rest waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertEqual(n1.receiving, n3)  # n1 trying to receive from n4
        self.assertTrue(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 stil on next mov statement
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 36)  # n2 has added
        self.assertEqual(n2.pc, 2)  # n2 moved onto jmp
        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertIsNone(n2.value_to_send)  # with nothing

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        # after 5 frames:
        # n2 has jumped, pc now points to the line AFTER the label
        # rest waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertEqual(n1.receiving, n3)  # n1 trying to receive from n4
        self.assertTrue(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 stil on next mov statement
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 36)  # n2 has added
        # n2 has jumped to after the label, points to mov (not executing yet)
        self.assertEqual(n2.pc, 4)
        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertIsNone(n2.value_to_send)  # with nothing

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        # after 6 frames:
        # n2 is now sending 36 to n4, n4 has yet to pick up
        # n2 pc still points to mov, has yet to increase, rest waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertEqual(n1.receiving, n3)  # n1 trying to receive from n4
        self.assertTrue(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 stil on next mov statement
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 36)  # n2 has added
        self.assertEqual(n2.pc, 4)  # still points to mov
        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertEqual(n2.sending, n4)  # n2 now sending to n4
        self.assertEqual(n2.value_to_send, 36)  # n2 sending 36 to n4

        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertFalse(n4.receiving_into_acc)  # n4 not receiving into acc
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send
        self.assertFalse(n3.receiving_into_acc)  # n3 not receiving into acc

        # after 7 frames:
        # n2 has now sent 36 to n4, n4 has picked up 36
        # the pc of n2 has increased beyond the mov, but n4 has NOT increased pc
        # n2 points to the first mov, but has not executed it yet
        # n4 is now sending 36 to n3, n3 has yet to pick up, rest waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertEqual(n1.receiving, n3)  # n1 trying to receive from n4
        self.assertTrue(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 stil on next mov statement
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 36)  # n2 has added
        self.assertEqual(n2.pc, 0)  # left the mov, now back to 0 (pointing)
        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not sending
        self.assertIsNone(n2.value_to_send)  # n2 has nothing to send

        self.assertEqual(n4.acc, 0)  # n4 got 36 from n2 but not into acc
        self.assertEqual(n4.pc, 0)  # n4 still on mov statement (sending)
        self.assertIsNone(n4.receiving)  # n4 received from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertFalse(n4.receiving_into_acc)  # n4 not receiving into acc
        self.assertEqual(n4.value_to_send, 36)  # n4 now sending 36

        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send
        self.assertFalse(n3.receiving_into_acc)  # n3 not receiving into acc

        # after 8 frames:
        # n4 has send 36 to n3, n3 has picked up and is sending 36 to n2
        # n4 pc has increased, n3 is still on the mov (now sending)
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertEqual(n1.receiving, n3)  # n1 trying to receive from n4
        self.assertTrue(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 2)  # n1 stil on next mov statement
        self.assertEqual(n1.acc, 4)  # n1 still has 4 in its acc

        self.assertEqual(n2.acc, 36)  # n2 has added
        self.assertEqual(n2.pc, 0)  # left the mov, now back to 0
        self.assertEqual(n2.receiving, n1)  # n2 receiving from n1
        self.assertTrue(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not sending
        self.assertIsNone(n2.value_to_send)  # n2 has nothing to send

        self.assertEqual(n4.acc, 0)  # n4 got 36 from n2 but not into acc
        self.assertEqual(n4.pc, 1)  # n4 has left the mov
        self.assertIsNone(n4.receiving)  # n4 received from n2
        self.assertIsNone(n4.sending)  # n4 has sent
        self.assertFalse(n4.receiving_into_acc)  # n4 not receiving into acc
        self.assertIsNone(n4.value_to_send)  # n4 not sending anymore

        self.assertEqual(n3.acc, 0)  # n3 received, but not into its acc
        self.assertEqual(n3.pc, 0)  # n3 still on that mov (sending now)
        self.assertIsNone(n3.receiving)  # n3 not receiving
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertEqual(n3.value_to_send, 36)  # n3 sending 36 to n1
        self.assertFalse(n3.receiving_into_acc)  # n3 not receiving into acc

        # after 9 frames:
        # n3 has sent to n1, now n3 pc has increased since n1 has picked it up
        # n1.acc is now 36 and it is about to add 4 to it
        # differences between this frame and frame 1:
        #   n1 contains 36 in its acc instead of 0
        #   n2 contains 36 in its acc instead of 0
        #   n3 pc points to the NOP (about to increase past)
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n1.sending)  # n1 not yet sending
        self.assertIsNone(n1.value_to_send)  # n1 not sending
        self.assertIsNone(n1.receiving)  # n1 has received
        self.assertFalse(n1.receiving_into_acc)  # into its acc
        self.assertEqual(n1.pc, 0)  # n1 points to start
        self.assertEqual(n1.acc, 36)  # n1 now has 36 in acc (received)

        self.assertEqual(n2.acc, 36)  # n2 has added
        self.assertEqual(n2.pc, 0)  # left the mov, now back to 0
        self.assertEqual(n2.receiving, n1)  # n2 receiving from n1
        self.assertTrue(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not sending
        self.assertIsNone(n2.value_to_send)  # n2 has nothing to send

        self.assertEqual(n4.acc, 0)  # n4 got 36 from n2 but not into acc
        self.assertEqual(n4.pc, 0)  # n4 has left the NOP, back to start
        self.assertEqual(n4.receiving, n2)  # n4 receiving from n2
        self.assertEqual(n4.sending, n3)  # n4 sending to n3
        self.assertFalse(n4.receiving_into_acc)  # n4 not receiving into acc
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send yet

        self.assertEqual(n3.acc, 0)  # n3 received, but not into its acc
        self.assertEqual(n3.pc, 1)  # n3 left mov, points to NOP
        self.assertIsNone(n3.receiving)  # n3 not receiving
        self.assertIsNone(n3.sending)  # n3 no longer sending
        self.assertIsNone(n3.value_to_send)  # n3 no longer sending
        self.assertFalse(n3.receiving_into_acc)  # n3 not receiving into acc

    
    def test_mov_with_delay(self):
        n1 = Node(0, 0)  # upper left node
        n2 = Node(0, 1)  # lower left node
        n3 = Node(1, 0)  # upper right node
        n4 = Node(1, 1)  # lower right node
        nodes = [n1, n2, n3, n4]
        main.build_io_tables(nodes)

        n1.lines = ["ADD 4", "MOV ACC, DOWN", "MOV RIGHT, ACC"]
        n2.lines = ["MOV UP, ACC", "ADD 32", "MOV ACC, RIGHT"]
        n4.lines = ["MOV LEFT, UP", "NOP"]
        n3.lines = ["MOV DOWN, LEFT", "NOP"]

        # frame 0:
        for n in nodes:  # set up and execute one frame
            n.parse_lines()
            self.assertTrue(n.is_valid)
            n.execute_next()

        # frame 1:
        # n1 has 4 in ACC
        self.assertEqual(n2.receiving, n1)  # n2 trying to receive from n1
        self.assertTrue(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though
        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        for n in nodes[1:]:
            self.assertEqual(n.pc, 0)  # the later 3 nodes have not moved pc
        self.assertEqual(n1.pc, 1)  # but n1 has moved on

        # frame 2:
        # n1 should move 4 down, which n2 picks up and puts into acc
        # n3 and n4 still waiting
        for n in nodes:
            n.execute_next()

        self.assertIsNone(n2.receiving)  # n2 no longer receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertEqual(n2.acc, 4)  # n2 got 4 into its acc
        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though
        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        self.assertEqual(n1.pc, 2)
        self.assertEqual(n2.pc, 1)
        self.assertEqual(n3.pc, 0)
        self.assertEqual(n4.pc, 0)

        # frame 3:
        # n1 now stuck trying to move in right, n2 adds, n3 and n4 wait

        for n in nodes:
            n.execute_next()

        self.assertIsNone(n2.receiving)  # n2 not receiving
        self.assertFalse(n2.receiving_into_acc)  # into its acc
        self.assertIsNone(n2.sending)  # n2 not trying to send to anyone
        self.assertEqual(n2.acc, 36)  # n2 added 32 to 4
        self.assertEqual(n4.receiving, n2)  # n4 trying to receive from n2
        self.assertEqual(n4.sending, n3)  # n4 trying to send to n3
        self.assertIsNone(n4.value_to_send)  # n4 has nothing to send though
        self.assertEqual(n3.receiving, n4)  # n3 trying to receive from n4
        self.assertEqual(n3.sending, n1)  # n3 trying to send to n1
        self.assertIsNone(n3.value_to_send)  # but has no value to send

        self.assertEqual(n1.pc, 2)
        self.assertEqual(n2.pc, 2)
        self.assertEqual(n3.pc, 0)
        self.assertEqual(n4.pc, 0)

        # frame 4:
        # n1 waiting, n2 moves 36 into n4, which moves that into n3,
"""

if __name__ == '__main__':
    unittest.main()
