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
    """

    # TODO: Create a static enum for modes
    def __init__(self, xpos, ypos):
        self.pos = (xpos, ypos)
        self.acc = 0
        self.bak = 0
        self.last = None
        self.mode = None
        self.lines = list()
        self.code = list()
        self.call_stack = list()
        self.inputs = {}
        self.outputs = {}
        print("Created Node at ", xpos, ypos)
    
    def build_io_tables(self):
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