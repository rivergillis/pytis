from node import Node

COLUMNS = 3
ROWS = 3

def build_io_tables(nodes):
    """ Assigns the LEFT, UP, DOWN, RIGHT values of each node's
    IO hash tables to the corresponding node objects.

    Strategy: Iterate through every node in the list
        for each node: iterate through every node in the list looking for
        xpos-1 = LEFT, xpos+1 = RIGHT, ypos-1 = UP, ypos+1 = DOWN
        The other position must remain unchanged, nodes without a matching
        adjencency will receive a NULL value for the node position
    """
    for current_assignment in nodes:
        for checking in nodes:
            if (checking.xpos == (current_assignment.xpos - 1) and checking.ypos == current_assignment.ypos):
                current_assignment.inputs["LEFT"] = checking
                current_assignment.outputs["LEFT"] = checking
            elif (checking.xpos == (current_assignment.xpos + 1) and checking.ypos == current_assignment.ypos):
                current_assignment.inputs["RIGHT"] = checking
                current_assignment.outputs["RIGHT"] = checking
            elif (checking.ypos == (current_assignment.ypos - 1) and checking.xpos == current_assignment.xpos):
                current_assignment.inputs["UP"] = checking
                current_assignment.outputs["UP"] = checking
            elif (checking.ypos == (current_assignment.ypos + 1) and checking.xpos == current_assignment.xpos):
                current_assignment.inputs["DOWN"] = checking
                current_assignment.outputs["DOWN"] = checking

def simulate():
    nodes = [Node(x,y) for x in range(COLUMNS) for y in range(ROWS)]
    print(nodes)

    build_io_tables(nodes)

    for node in nodes:
        node.print_adjacency()


if __name__ == "__main__":
    simulate()