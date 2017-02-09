from node import Node

def simulate():
    COLUMNS = 3
    ROWS = 3

    node_list = [[Node(x,y) for x in range(COLUMNS)] for y in range(ROWS)]
    print(node_list)


if __name__ == "__main__":
    simulate()