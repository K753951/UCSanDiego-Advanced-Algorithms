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


def add_capacity(road_pointer, master_list):
    """ Finds the road with the max (capacity - flow) along the path from road_pointer to capitol. Updates flows
    of all roads along path. Updates capacity of residual roads. Returns the flow that has been added. """

    # Make a list to hold remaining capacities of roads along the path.
    capacity = []

    # Make a list to hold path.
    path = []

    while True:
        # First, find the entry for road in the master list.
        node = master_list.master[road_pointer]

        # Add the remaining capacity of the terminal node to the capacity list.
        remaining_capacity = node.capacity - node.flow
        capacity.append(remaining_capacity)

        # Add the node to the path list.
        path.append(node)

        # Find if the node has a parent. If yes, set road_pointer to point to this entry in the master list
        # and continue looping. If no, break.
        if node.parent is not None:
            p = master_list.master[node.parent]
            if p.capacity - p.flow > 0:
                road_pointer = node.parent

            # If we have reached this point without moving to the parent, there is no path. Return 0.
            else:
                return 0
        else:
            break

    # Find the max remaining capacity.
    maximum = min(capacity)

    # Update the flows of all nodes along the path and their residual nodes.
    for x in path:

        # Update the flow.
        x.flow += maximum

        # Update the capacity of the residual.
        res = master_list.master[x.pointer]
        res.capacity += maximum

    return maximum


def find_path_capacity(masterlist, ez, n):
    """ Finds the maximum capacity of a path through the graph and updates flows to utilize this path.
    Returns the amount of flow added. """
    # Make an instance of the QueueFrontier class to find shortest paths.
    queue = QueueFrontier()

    # Make a list to hold previously explored roads to avoid loops.
    explored = []

    # Use a BFS algorithm to explore paths.
    # Add all roads starting at the city to be evacuated (city 1) to the queue.
    if ez.numpy_array[1] is not None:
        for road in ez.numpy_array[1]:
            r = masterlist.master[road]
            if r.capacity - r.flow > 0:
                queue.add_to_queue(road)

                # Add the road to the explored list.
                explored.append(road)

                # Ensure the parent of these nodes is None.
                masterlist.master[road].parent = None

    # Pop roads from the queue. If the road does not lead the the final destination, add its children to the queue.
    while True:
        # If the queue is empty and we haven't returned a path, return 0 - no path exists.
        if len(queue.queue) is 0:
            return 0

        # Pop a node from the queue.
        popped = queue.pop()

        # Find the road record for the index that was popped.
        current_road = masterlist.master[popped]

        # If the road ends at the evacuation site, find the max capacity that can be added. Add this to total capacity.
        if current_road.end == n:
            amount_to_add = add_capacity(popped, masterlist)
            return amount_to_add

        # Add all outgoing roads from end city to the queue. Update their parent pointers to point to popped.
        elif ez.numpy_array[current_road.end] is not None:
            for element in ez.numpy_array[current_road.end]:

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


# Build a MasterList to hold paths and their capacities.
roads = MasterList()

# Add roads and their capacities to the master list.
with open(sys.argv[1]) as input_file:
    first_line = input_file.readline()
    space = first_line.find(" ")
    global N
    N = int(first_line[:space])             # N = number of cities
    backslashn = first_line.rfind("\n")
    global M
    M = int(first_line[space + 1:backslashn])   # M = number of roads

    # Check for valid input.
    if N < 1 or N > 100:
        raise Exception("Invalid number of cities")
    if M < 0 or M > 10000:
        raise Exception("Invalid number of roads")

    # Make an instance of the EasyAccess array.
    global easy
    easy = EasyAccess(N + 1)

    # Read the road information from the remaining lines and add to the MasterList "Roads".
    counter = 0
    for i in range(M):
        road_stats = input_file.readline()
        first_space = road_stats.find(" ")
        second_space = road_stats.find(" ", first_space + 1)
        backslash = road_stats.rfind("\n")
        start_city = int(road_stats[:first_space])
        end_city = int(road_stats[first_space + 1:second_space])
        cap = int(road_stats[second_space + 1:backslash])

        roads.add_node(index=counter, start=start_city, end=end_city, capacity=cap)

        # Add data for both road and residual edge to easy access array.
        easy.add_entry(start_city, counter)
        easy.add_entry(end_city, counter + 1)

        counter += 2


# Make a variable to hold the total evacuation capacity. Set to 0.
total_capacity = 0

# Continue to find paths and add capacities to total until no more paths found.
returned = None
while returned is not 0:
    returned = find_path_capacity(roads, easy, N)
    total_capacity += returned


print(total_capacity)
