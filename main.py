from node import Node

COLUMNS = 3
ROWS = 3


def load_nodes(filename):
    """ Loads a set of nodes in from filename """
    with open(filename) as f:
        content = f.readlines()
    # remove whitespace
    content = [x.strip() for x in content]

    nodes = []
    node_count = -1

    for line in content:
        # start of a new node
        if line.startswith("["):
            temp = line.replace(" ", "")
            nodes.append(Node(int(temp[1]), int(temp[3])))
            node_count += 1
        # not whitespace
        elif line:
            nodes[node_count].lines.append(line)

    for node in nodes:
        print(node)
        print(node.lines)
    return nodes


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
                current_assignment.adjacency["LEFT"] = checking
            elif (checking.xpos == (current_assignment.xpos + 1) and checking.ypos == current_assignment.ypos):
                current_assignment.adjacency["RIGHT"] = checking
            elif (checking.ypos == (current_assignment.ypos - 1) and checking.xpos == current_assignment.xpos):
                current_assignment.adjacency["UP"] = checking
            elif (checking.ypos == (current_assignment.ypos + 1) and checking.xpos == current_assignment.xpos):
                current_assignment.adjacency["DOWN"] = checking


def update_output_table(nodes, pipes):
    """
    Iterates through every node and updates """


def simulate():
    nodes = load_nodes("nodes.txt")
    #nodes = [Node(x, y) for x in range(COLUMNS) for y in range(ROWS)]

    build_io_tables(nodes)

    for node in nodes:
        # node.print_adjacency()
        node.execute_next()


if __name__ == "__main__":
    simulate()
