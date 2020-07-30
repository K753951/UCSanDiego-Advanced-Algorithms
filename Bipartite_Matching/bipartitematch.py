import sys
import numpy as np


class Node:
    def __init__(self, index, start, end, capacity, flow, pointer, parent):
        self.index = index
        self.start = start
        self.end = end
        self.capacity = capacity
        self.flow = flow
        self.pointer = pointer
        self.parent = parent


class MasterList:
    """ Stores information for all roads. A static data structure. """
    def __init__(self):
        self.master = []

    def add_node(self, index, start, end, capacity):
        new_node = Node(index=index, start=start, end=end, capacity=capacity, flow=0, pointer=index + 1, parent=None)
        self.master.append(new_node)
        residual = Node(index=index + 1, start=end, end=start, capacity=0, flow=0, pointer=index, parent=None)
        self.master.append(residual)


class QueueFrontier:
    """ A dynamic data structure used to repeatedly find paths between cities. """
    def __init__(self):
        self.queue = []

    def add_to_queue(self, pointer):
        self.queue.append(pointer)

    def pop(self):
        node = self.queue[0]
        self.queue = self.queue[1:]
        return node


class EasyAccess:
    """ A 2D numpy array to hold pointers to roads that start/end at particular cities. Row index corresponds to
    index of starting city. Column index corresponds to index of ending city. """
    def __init__(self, n):
        self.numpy_array = np.empty(n, dtype=list)

    def add_entry(self, start, pointer):
        if self.numpy_array[start] is None:
            new_list = [pointer]
            self.numpy_array[start] = new_list
        else:
            list_pointer = self.numpy_array[start]
            list_pointer.append(pointer)


def get_path(node_pointer, m_list):
    """ Finds the road with the max (capacity - flow) along the path from road_pointer to capitol. Updates flows
    of all roads along path. Updates capacity of residual roads. Returns the flow that has been added. """

    # Make a list to hold remaining capacities of roads along the path.
    capacity = []

    # Make a list to hold path.
    path = []

    # Make a list to hold path indexes.
    path_indexes = []

    while True:
        # First, find the entry for road in the master list.
        node = m_list.master[node_pointer]

        # Add the remaining capacity of the terminal node to the capacity list.
        remaining_capacity = node.capacity - node.flow
        capacity.append(remaining_capacity)

        # Add the node to the path list.
        path.append(node)
        path_indexes.append(node.index)

        # Find if the node has a parent. If yes, set road_pointer to point to this entry in the master list
        # and continue looping. If no, break.
        if node.parent is not None:
            p = m_list.master[node.parent]
            if p.capacity - p.flow > 0:
                node_pointer = node.parent

            # If we have reached this point without moving to the parent, there is no path. Return 0.
            else:
                return None
        else:
            break

    # Find the max remaining capacity.
    maximum = min(capacity)

    # Update the flows of all nodes along the path and their residual nodes.
    for x in path:

        # Update the flow.
        x.flow += maximum

        # Update the capacity of the residual.
        res = m_list.master[x.pointer]
        res.capacity += maximum

    return path_indexes


def find_path_capacity(masterlist, ez, n):
    """ Finds the maximum capacity of a path through the graph and updates flows to utilize this path.
    Returns the amount of flow added. """
    # Make an instance of the QueueFrontier class to find shortest paths.
    queue = QueueFrontier()

    # Make a list to hold previously explored roads to avoid loops.
    explored = []

    # Use a BFS algorithm to explore paths.
    # Add all edges beginning at start to the queue.
    if ez.numpy_array[0] is not None:
        for edge in ez.numpy_array[0]:
            r = masterlist.master[edge]
            if r.capacity - r.flow > 0:
                queue.add_to_queue(edge)

                # Add the road to the explored list.
                explored.append(edge)

                # Ensure the parent of these nodes is None.
                masterlist.master[edge].parent = None

    # Pop roads from the queue. If the road does not lead the the final destination, add its children to the queue.
    while True:
        # If the queue is empty and we haven't returned a path, return 0 - no path exists.
        if len(queue.queue) is 0:
            return None

        # Pop a node from the queue.
        popped = queue.pop()

        # Find the road record for the index that was popped.
        current_edge = masterlist.master[popped]

        # If the road ends at the evacuation site, find the max capacity that can be added. Add this to total capacity.
        if current_edge.end == n:
            pathway = get_path(popped, masterlist)
            return pathway

        # Add all outgoing roads from end city to the queue. Update their parent pointers to point to popped.
        elif ez.numpy_array[current_edge.end] is not None:
            for element in ez.numpy_array[current_edge.end]:

                # Check if element has a capacity and has not previously been explored.
                record = masterlist.master[element]
                if record.capacity is not 0 and record.index not in explored:

                    # Check if element's capacity has not been used up. If some capacity left, add index to queue.
                    if record.capacity - record.flow > 0:
                        queue.add_to_queue(element)

                        # Update parent of added node.
                        record.parent = popped

                        # Add the new node to the explored list.
                        explored.append(record.index)


# Read data from input file.
with open(sys.argv[1]) as input_file:

    # Get the number of flights and crews from the first line.
    first_line = input_file.readline()
    first_space = first_line.find(" ")
    backslashn = first_line.find("\n")
    global flights
    flights = int(first_line[:first_space])
    global crews
    crews = int(first_line[first_space + 1:backslashn])

    # Check for proper usage.
    if flights < 1 or flights > 100:
        raise Exception("Invalid number of flights")
    if crews < 1 or crews > 100:
        raise Exception("Invalid number of crews")

    # Create edges from data.
    global data
    data = np.empty([flights, crews], dtype=int)
    for i in range(flights):
        next_line = input_file.readline()
        previous_space = -1
        for j in range(crews):
            if j < crews - 1:
                space = next_line.find(" ", previous_space + 1)
                integer = int(next_line[previous_space + 1:space])
                previous_space = space
                data[i][j] = integer
            elif j == crews - 1:
                backslash = next_line.find("\n")
                integer = int(next_line[previous_space + 1:backslash])
                data[i][j] = integer

# Make a masterlist to hold flight data.
master_list = MasterList()

# Make an easyaccess array to hold node data.
num_nodes = flights + crews + 2
easy = EasyAccess(num_nodes)

# Add edges to graph and to easyaccess array.
counter = 0
for i in range(flights):
    for j in range(crews):
        if data[i][j] == 1:
            master_list.add_node(index=counter, start=i + 1, end=j + flights + 1, capacity=1)
            easy.add_entry(start=i + 1, pointer=counter)
            easy.add_entry(start=j + flights + 1, pointer=counter + 1)
            counter += 2

# Add paths connecting start (index=0) to all flights. Add paths connecting all crews to
# end (index=flights*crews).
s = 0
e = flights + crews + 1

for i in range(flights):
    master_list.add_node(index=counter, start=s, end=i + 1, capacity=1)
    easy.add_entry(start=s, pointer=counter)
    easy.add_entry(start=i + 1, pointer=counter + 1)
    counter += 2

for j in range(crews):
    master_list.add_node(index=counter, start=j + flights + 1, end=e, capacity=1)
    easy.add_entry(start=j + flights + 1, pointer=counter)
    easy.add_entry(start=e, pointer=counter + 1)
    counter += 2

# Make a list to hold paths.
path_list = []

# Continue to find paths between flights and crews until no more paths found.
returned = -1
while returned is not None:
    returned = find_path_capacity(master_list, easy, e)
    if returned is not None:
        path_list.extend(returned)

# Make an array initialized to -1 to hold output data (crew numbers).
output = np.full(flights, -1)

# Make a new list to hold valid paths.
new_list = []

for current_edge in path_list:
    crew = master_list.master[current_edge].end
    crew_id = master_list.master[current_edge].end - flights
    flight = master_list.master[current_edge].start

    # First, only consider edges between valid flights and crews (no edges connecting to source or sink).
    if flight != 0 and crew != 0 and flight != e and crew != e:

        # Only consider true edges (not residual edges).
        if 0 < flight <= flights < crew < e:

            # Find if edge has been cancelled by residual flow.
            edge_count = path_list.count(current_edge)
            r = master_list.master[current_edge].pointer
            residual_count = path_list.count(r)

            # Add edge to new list only if it has not been cancelled by the presence of residual edge(s).
            if edge_count > residual_count and current_edge not in new_list:
                new_list.append(current_edge)

# Convert
for y in new_list:
    f = master_list.master[y].start
    c = master_list.master[y].end
    output[f - 1] = c - flights

# Convert output to correct format.
for i in range(flights):
    print(output[i], end=" ")
print("\n")







