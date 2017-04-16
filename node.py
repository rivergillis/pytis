""" This file contains all of the implementation for
    the Node object. I/O can be handled as an input/output
    hash table that is built for each of the surrounding nodes.
    The main program will operate by calling all of the I/O functions
    sequentially (possibly twice over).
"""

# TODO: currently the nodes are executed sequentially, which causes IO
# problems due to IO revolving around receiving something. May need 2-pass
# for MOV instructs in simulate next frame.


class Node(object):

    """ The node object represents the squares containing code
    Each node has a list of lines of code as a list of strings
    A call stack, that is the parsed form of those lines
    An accumulator value, a bak value, a Last value
    A state value, and an idle percentage value

    Input is handled by a list of 4 values representing
    the input in clockwise fashion (0 being up, 3 being left)
    output is handled in the same fashion

    code contains a dict of tuples representing instructions parsed from lines
        each code is a 3-tuple containing three 'arguments'
        The first argument is the opcode, representing which operation to execute
        The next two arguments are used for registers or immediates to the opcode
            Any empty argument space is set to None
        The keys for the code dict correspond to the line number
            This is necessary as labels will cause an offset between list index and actual line number
            This is used in conjuction with the program conter to determine which instruction to execute

    labels contains a dict of string->integer pairs
        The string is the label, and the integer is the corresponding line number
    """

    VALID_INSTRUCTIONS = dict([("NOP", 1), ("MOV", 3), ("SWP", 1), ("SAV", 1),
                               ("ADD", 2), ("SUB", 2), ("NEG", 1), ("JMP", 2),
                               ("JEZ", 2), ("JNZ", 2), ("JGZ", 2), ("JLZ", 2),
                               ("JRO", 2)])

    VALID_REGISTERS = ["ACC", "NIL", "LEFT",
                       "RIGHT", "UP", "DOWN", "ANY", "LAST"]

    # TODO: Create a static enum for modes
    def __init__(self, xpos, ypos):
        self.full_debug = False

        self.xpos = xpos
        self.ypos = ypos
        self.acc = 0
        self.bak = 0
        self.last = None
        self.mode = None
        self.lines = list()
        self.code = dict()
        self.call_stack = list()
        self.labels = dict()
        self.is_valid = True
        self.adjacency = {"LEFT": None,
                          "RIGHT": None, "UP": None, "DOWN": None}

        self.pc = 0  # program counter

        # sending/receiving point to a Node that we are sending/receiving to/from
        # if either is None, we are not sending or receiving from anyone
        self.sending = None
        self.receiving = None

        self.receiving_into_acc = False
        self.value_to_send = None
        # print("Created Node at ", xpos, ypos)

    def validate_code(self):
        """ Validates that instructions are
        syntactically correct
        """
        # iterate through every instruction in code
        for instruction in self.code.values():
            instruct_len = 0
            args = []
            # get the length of the instruction in args
            for i in instruction:
                if (i):
                    args.append(i)
                    instruct_len += 1
            # the first arg is the opcode
            opcode = instruction[0]
            # print(self.code)
            # print(instruction)
            # print(opcode)

            # invalid if any argcount is not correct
            if (Node.VALID_INSTRUCTIONS.get(opcode, -1) != instruct_len):
                print("length mismatch!", opcode)
                print("length ", instruct_len, " expected ",
                      Node.VALID_INSTRUCTIONS.get(opcode, -1))
                print(instruction)
                self.is_valid = False
                return
            # ADD/SUB needs a register or a number, as does JRO
            if (opcode == "ADD" or opcode == "SUB" or opcode == "JRO"):
                if (type(args[1]) == int):
                    continue
                elif (args[1] not in Node.VALID_REGISTERS):
                    self.is_valid = False
                    return
            # MOV needs a register (but the first arg can be numeric)
            elif (opcode == "MOV"):
                if ((type(args[1]) != int and args[1] not in Node.VALID_REGISTERS) or args[2] not in Node.VALID_REGISTERS):
                    self.is_valid = False
                    return
            # J needs a label
            elif (opcode.startswith("J")):
                if (args[1] not in self.labels.keys()):
                    print('label ', args[1], ' not in labels dict')
                    self.is_valid = False
                    return

    def parse_lines(self):
        """ Parses the string lines to be
            placed onto the call stack
            note: doesn't support multiple spaces yet
        """
        # iterate through every string of code
        for line_num, line in enumerate(self.lines):
            # This is a label on a line by itself
            if (line.strip().endswith(':')):
                stripped = line.strip().replace(':', '')
                # If we redefine a label, this is invalid code
                if (self.labels.get(stripped, False)):
                    self.is_valid = False
                    return
                # Otherwise, save the label, line_num pair in labels dict
                self.labels[stripped] = line_num
                continue

            instruction = tuple()
            # remove commas and split on spaces
            # TODO: handle commas with no spaces
            args = line.replace(",", "").split(" ")
            # each instruction gets a spot for 3 args (including opcode)
            for i in range(3):
                # Any empty args get None
                if (i > len(args) - 1):
                    instruction += (None,)
                else:
                    # Add the arg, make it numeric if possible
                    try:
                        instruction += (int(args[i]),)
                    except ValueError:
                        instruction += (args[i],)
            self.code[line_num] = instruction
        self.validate_code()

    def increment_pc(self):
        """ Updates the pc according to the current status of
            the pc and the number of lines of code we have

            If the line after incrementing the pc consists of only a label
            we call increment_pc() again
        """
        # Increase if we have some code
        if (self.code):
            self.pc += 1
        # If our current line number is >= max line nums, reset pc
        if (self.pc >= len(self.lines)):
            self.pc = 0

        # increment the pc again if the new line of code is only a label
        if self.code.get(self.pc, False) == False:
            self.increment_pc()

    def send_value(self):
        """ Sends a value from the self node to the sending node
            This is only called by the receiving node!
            Return value_to_send if successful
            Return None if the node we send to is not receiving from us
        """
        print("In send_value() for ", str(self))
        print("We want to send to ", str(self.sending))
        # check if the node we are sending to is receiving from us
        if ((self.sending.receiving == self) and (self.value_to_send)):
            self.increment_pc()  # we are done after any send
            return self.value_to_send
        else:
            if (not self.sending.receiving == self):
                print("The node we're sending to is not receiving us!")
            else:
                print("We don't have a value to send!")
            return None

    def receive_value(self):
        """ Receives a value from node receiving into register reg
            If the other node is not sending, return False
                Otherwise receive the value and return True

            Idea: a node loops on a mov until it is succesful
                upon success, increment the pc
        """
        print("In receive_value() for ", str(self))
        print("We want to receive from ", str(self.receiving))
        # have to check if the node we receive from is sending to us
        if (self.receiving.sending == self):
            # get the value from the other node
            value = self.receiving.send_value()
            print("got ", value, " from our receiving node")

            if (not value):  # The node is sending but does not have its value ready yet
                return False

            # The node we received from is now no longer sending to anyone
            self.receiving.sending = None
            self.receiving.value_to_send = None

            # This node is no longer receiving from anyone
            self.receiving = None

            # assign the value to the correct register
            if (self.receiving_into_acc):
                # we are sending this value to our acc
                self.acc = value
                self.receiving_into_acc = False
                # if we receive into the acc, we are done and can move the pc
                # up
                self.increment_pc()
            else:
                # We are sending this value to another node
                self.value_to_send = value
                # TODO: add in the rest of the registers
            return True
        else:
            # the other node is not sending to us
            print("Our node we want to receive from is not sending to us!")
            return False

    def execute_next(self):
        """ Executes the next instruction
            that the program counter points to
        """
        if (self.full_debug):
            print("Entering execute_next() for node ", self)

        if (self.receiving):
            self.receive_value()
            # If we succesfully receive, we want to increment the PC, but only
            # if we are not sending
            if (not self.receiving):
                # if (not self.sending):
                #    print("Succesfully completed a MOV onto ", self)
                #    self.increment_pc()
                return

        if (self.receiving or self.sending):
            if (self.receiving):
                print("Currently receiving in execute_next(), now returning")
            if (self.sending):
                print("Currently sending in execute_next(), now returning")
            return
        # if (self.receiving or self.sending):
        # return  # we don't do anything if IO is happening TODO: but we
        # should, right?

        instruction = self.code.get(self.pc, False)
        # print(instruction)
        if (instruction == False):
            # If we have some code, then this is a label and we need to increment pc
            # if timing is in error, call execute_next() again here
            self.increment_pc()
            return

        # grab the next instruction
        opcode = instruction[0]

        # print(instruction)

        # Ties opcodes to functions
        if (opcode == "ADD"):
            self.add(instruction[1])
        elif (opcode == "SUB"):
            self.sub(instruction[1])
        elif (opcode == "NEG"):
            self.neg()
        elif (opcode == "SAV"):
            self.sav()
        elif (opcode == "SWP"):
            self.swp()

        # Jumping args should return so we don't mess with the pc
        elif (opcode == "JMP"):
            self.jmp(instruction[1])
            return
        elif (opcode == "JEZ"):
            self.jez(instruction[1])
            return
        elif (opcode == "JNZ"):
            self.jnz(instruction[1])
            return
        elif (opcode == "JLZ"):
            self.jlz(instruction[1])
            return
        elif (opcode == "JGZ"):
            self.jgz(instruction[1])
            return
        elif (opcode == "JRO"):
            self.jro(instruction[1])
            return

        elif (opcode == "MOV"):
            self.mov(instruction[1], instruction[2])
            return

        elif (opcode == "NOP"):
            self.increment_pc()  # Skip this instruction. Consider changing to ADD NIL
            return

        self.increment_pc()

    def mov(self, reg1, reg2):
        """ Moves the value from reg1 into reg2
        if reg1 is a port (U/D/L/R) we receive from that Node
        if reg2 is a port (U/D/L/R) we send to that Node
        syntax: MOV <r1, r2> for registers r1 and r2
        """
        print("Executing mov on node ", str(self),
              " with reg1=", reg1, " reg2=", reg2)
        if reg1 in self.adjacency.keys():
            # This is a node we need to receive from
            self.receiving = self.adjacency[reg1]
            print("we need to receive from ", str(self.receiving))
            # somehow set our send value?
        else:
            # This is this node's registers (ACC,etc)
            if reg1 == "ACC":
                self.value_to_send = self.acc
                print("received from ACC, now sending value ", self.value_to_send)
            # Or reg1 was a literal
            elif type(reg1) == int:
                self.value_to_send = reg1
                print("received from literal, now sending value ",
                      self.value_to_send)

        if reg2 in self.adjacency.keys():
            # This is a node we need to send to
            self.sending = self.adjacency[reg2]
            print("now sending to ", str(self.sending))
        else:
            # This is this node's registers (ACC, etc)
            if reg2 == "ACC":
                self.receiving_into_acc = True
                print("Set to receive into our ACC")

        print("initial mov call finished on ", str(self))
        self.execute_next()  # we need to use one extra clock cycle

    def sav(self):
        """ The value of ACC is written to BAK
        syntax: SAV
        """
        self.bak = self.acc

    def swp(self):
        """ The value of BAK is written to the ACC
        syntax: SWP
        """
        self.acc = self.bak

    def add(self, val):
        """ Adds a value to the accumulator
        This is done using ADD <x>
        Where x can be a Node or a value
        """
        if (type(val) == Node):
            literal = self.get_input(val)
            self.add(literal)
        else:
            self.acc += val

    def sub(self, val):
        """ Subtracts a value from the accumulator
        syntax: SUB <x>
        Where x can be a Node or a value
        """
        if (type(val) == Node):
            literal = self.get_input(val)
            self.sub(literal)
        else:
            self.acc -= val

    def neg(self):
        """ Negates ACC
        syntax: NEG
        """
        self.acc *= -1

    def jmp(self, label):
        """ Changes the pc to point to the line on which the
        label *label* resides.
        syntax: JMP <l> where l is a label """
        self.pc = self.labels[label]

    def jez(self, label):
        """ Jumps to label if acc is equal to Zero
        syntax: JEZ <l>
        """
        if (self.acc == 0):
            self.jmp(label)
        else:
            self.increment_pc()

    def jnz(self, label):
        """ Jumps to label if acc is not equal to zero
        syntax: JNZ <l>
        """
        if (self.acc != 0):
            self.jmp(label)
        else:
            self.increment_pc()

    def jlz(self, label):
        """ Jumps to label is acc is less than zero
        syntax: JLZ <l>
        """
        if (self.acc < 0):
            self.jmp(label)
        else:
            self.increment_pc()

    def jgz(self, label):
        """ Jumps to label is acc is greater than zero
        syntax: JGZ <l>
        """
        if (self.acc > 0):
            self.jmp(label)
        else:
            self.increment_pc()

    def jro(self, target):
        """ Jumps to the offset specified by target
        syntax: JRO <t> where t can be an integer or a register
        Ex: JRO 0 halts execution
            JRO 2 skips the next instruction
            JRO -1 executes the previous instruction next
            JRO ACC uses the value in ACC to specify the offset
        """
        if (type(target) == int):
            self.pc += target
        elif (target == "ACC"):
            self.pc += self.acc
            # TODO: account for sending the pc over the max lines of code (and
            # under!)
        else:
            # TODO: add support for UP/DOWN/etc
            pass

    def __str__(self):
        s = "Node at (" + str(self.xpos) + "," + str(self.ypos) + ")"
        s += " ACC: " + str(self.acc) + " BAK: " + \
            str(self.bak) + " pc: " + str(self.pc)
        if (not self.is_valid):
            s += " INVALID CODE"
        return s

    def print_adjacency(self):
        for k, v in self.adjacency.items():
            if (v != None):
                print("Node at ", self.xpos, self.ypos,
                      " has node ", k, " at ", v.xpos, v.ypos)
            else:
                print("Node at ", self.xpos, self.ypos, " has no node ", k)
