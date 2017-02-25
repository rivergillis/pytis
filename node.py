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

    The call stack is a list of triplets where the first term is
    the instruction and the next two terms are arguments, for instructions with
    less than two arguments, the extra fields are None.
    Arguments are stored as numeric types when possible.
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
        self.code = list()
        self.call_stack = list()
        self.labels = list()
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
        for instruction in self.code:
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
                print("length mismatch!")
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
                if (args[1] not in self.labels):
                    self.is_valid = False
                    return

    def parse_lines(self):
        self.code = list()
        """ Parses the string lines to be
            placed onto the call stack
            note: doesn't support multiple spaces yet
        """
        # iterate through every string of code
        for line in self.lines:
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
            self.code.append(instruction)
        self.validate_code()

    def execute_next(self):
        """ Executes the next instruction
            that the program counter points to
        """
        # return if empty node
        if (not self.code):
            return

        # grab the next instruction
        instruction = self.code[self.pc]
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

        # increment pc and set to start if we've gotten to the end
        self.pc += 1
        if (self.pc >= len(self.code)):
            self.pc = 0

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
