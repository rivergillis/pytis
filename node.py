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
        self.adjacency = {"LEFT": None, "RIGHT": None, "UP": None, "DOWN": None}
        print("Created Node at ", xpos, ypos)

    def parse_lines(self):
        self.code = list()
        """ Parses the string lines to be
            placed onto the call stack
        """
        for line in self.lines:
            instruction = tuple()
            args = line.split(" ")
            for i in range(3):
                if (i > len(args)-1):
                    instruction += (None,)
                else:
                    try:
                        instruction += (int(args[i]),)
                    except ValueError:
                        instruction += (args[i],)
            self.code.append(instruction)

    
    def execute_next(self):
        """ Executes the next instruction
            on the call stack
        """
        pass

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
    
    def add(self, val):
        """ Adds a value to the accumulator
        This is done using ADD <x>
        Where x can be a Node or a value
        """
        if (type(val) == Node):
            literal = self.get_input(val)
            self.add(literal)
        else:
            acc += val

    def sub(self, val):
        """ Subtracts a value from the accumulator
        syntax: SUB <x>
        Where x can be a Node or a value
        """
        if (type(val) == Node):
            literal = self.get_input(val)
            self.sub(literal)
        else:
            acc -= val

    def neg(self):
        """ Negates ACC
        syntax: NEG
        """
        acc *= -1

    def print_adjacency(self):
        for k,v in self.adjacency.items():
            if (v != None):
                print("Node at ", self.xpos, self.ypos, " has node ", k, " at ", v.xpos, v.ypos)
            else:
                print("Node at ", self.xpos, self.ypos, " has no node ", k)