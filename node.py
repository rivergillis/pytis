""" This file contains all of the implementation for
    the Node object. I/O can be handled as an input/output
    hash table that is built for each of the surrounding nodes.
    The main program will operate by calling all of the I/O functions
    sequentially (possibly twice over).
"""


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
        #print("Created Node at ", xpos, ypos)

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
            # ADD/SUB needs a register or a number
            if (opcode == "ADD" or opcode == "SUB"):
                if (type(args[1]) == int):
                    continue
                elif (args[1] not in Node.VALID_REGISTERS):
                    self.is_valid = False
                    return
            # MOV needs a register
            elif (opcode == "MOV"):
                if (args[1] not in Node.VALID_REGISTERS or args[2] not in Node.VALID_REGISTERS):
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
        """
        # Increase if we have some code
        if (self.code):
            self.pc += 1
        # If our current line number is >= max line nums, reset pc
        if (self.pc >= len(self.lines)):
            self.pc = 0

    def execute_next(self):
        """ Executes the next instruction
            that the program counter points to
        """
        # return if empty node
        instruction = self.code.get(self.pc, False)
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
            # TODO
            return

        elif (opcode == "NOP"):
            self.increment_pc()  # Skip this instruction. Consider changing to ADD NIL
            return

        self.increment_pc()

    def send_output(self, node):
        """ Returns an output to another
        node
        """
        return self.outputs[node]

    def get_input(self, node):
        """ Calls another node's
        get_output method to request an output
        from another node
        """
        return node.send_output(self)

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
