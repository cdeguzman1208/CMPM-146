# imports
from heapq import heappop, heappush     # heap queue library
from math import sqrt                   # math library

# find_path()
# Note that this function is being called in nm_interactive.py
def find_path(source_point, destination_point, mesh):

    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:
        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    path = []
    boxes = {}
    
    path, boxes = bidirectional_a_star(source_point, destination_point, mesh)

    return path, boxes.keys()

# find boxes()
# Identify the source and destination boxes.
def find_boxes(src, dst, mesh):
    source_box = None
    destination_box = None
    # Scan through the list of boxes to find which contains the source point.
    for box in mesh['boxes']:
        if source_box is None and box[0] <= src[0] <= box[1] and box[2] <= src[1] <= box[3]:
            source_box = box
        # Do this as well for the destination point.
        if destination_box is None and box[0] <= dst[0] <= box[1] and box[2] <= dst[1] <= box[3]:
            destination_box = box
        if not (source_box is None or destination_box is None):
            break
    # return a list of these two boxes.
    return source_box, destination_box

# get_detail_point()
def get_detail_point(current_pt, next_box):
    x = min(max(current_pt[0], next_box[0]), next_box[1])
    y = min(max(current_pt[1], next_box[2]), next_box[3])
    return x, y

# simple_search() -> a_star() -> bidirectional_a_star()
# Implement the simplest complete search algorithm you can.
# Modify your simple search to compute a legal list of line segments demonstrating the path.
# Modify the supplied Dijkstra's implementation into an A* implementation.
# Modify your A* into a bidirectional A*.
def bidirectional_a_star(src, dst, mesh):

    # INITIALIZATION
    src_box, dst_box = find_boxes(src, dst, mesh)   # identifies the boxes containing the source and destination points in the mesh
    if src_box is None or dst_box is None:          # if either the source or destination box is not found,
        print("No source/destination box!")         # the function prints an error message
        return [], {}                               # and returns an empty path and an empty dictionary
    
    # DISTANCE AND HEURISTIC FUNCTIONS
    def distance(start, end):                       # computes the Euclidean distance between two points
        return sqrt(((end[0] - start[0]) ** 2) + ((end[1] - start[1]) ** 2))

    def heuristic(point, dest):                     # computes the heuristic (estimated cost) from a point to the destination
        return distance(point, dest)
    
    # VARIABLES INITIALIZATION
    path = []                                       # store the final path (detailed points)
    box_path = []                                   # and the path in terms of boxes
    boxes = {src_box: src}                          # a dictionary that maps boxes to detailed points

    frontier = []                                   # a priority queue that stores nodes for exploration
    heappush(frontier, (0, src_box, dst))           # initialized with the source
    heappush(frontier, (0, dst_box, src))           # and destination nodes

    # FORWARD AND BACKWARD TRACKING
    forward_prev = {src_box: None}                  # are dictionaries that store the parent box for each box in the forward
    backward_prev = {dst_box: None}                 # and backward search

    dist_so_far = {src_box: 0}                      # store the cumulative distances from the source
    dist_from_dst = {dst_box: 0}                    # and destination

    # MAIN LOOP
    while frontier:                                 # continues until the frontier is not empty
        priority, b, target = heappop(frontier)     # in each iteration, a node is popped from the frontier
        entry_point = None

        # checks whether the current node corresponds to the source or destination
        # and determines the entry point into the mesh
        if target == dst:
            entry_point = src
            parent_forward = forward_prev[b]
            if not (parent_forward is None):
                entry_point = get_detail_point(boxes[parent_forward], b)
        elif target == src:
            entry_point = dst
            parent_backward = backward_prev[b]
            if not (parent_backward is None):
                entry_point = get_detail_point(boxes[parent_backward], b)

        boxes[b] = entry_point  # if the entry point is found, it reconstructs the path in terms of boxes and detailed points

        # PATH RECONSTRUCTION
        # the final path is reconstructed by traversing the box_path and appending detailed points to the path
        if (target == dst and b in backward_prev) or (target == src and b in forward_prev):
            a = b
            while not (a is None):
                box_path.append(a)
                a = forward_prev[a]
            while not (b is None):
                box_path.insert(0, b)
                b = backward_prev[b]

            pt = dst
            for box in box_path:
                path.append(pt)
                pt = get_detail_point(pt, box)
            path.append(pt)
            path.append(src)
            break

        # continue exploring neighbors and updating distances until a valid path is found
        # or the frontier is exhausted
        for c in mesh['adj'][b]: 
            if target == dst:
                child_entry = get_detail_point(boxes[b], c)
                dist_to_child = dist_so_far[b] + distance(boxes[b], child_entry)
                child_priority = dist_to_child + heuristic(child_entry, target)

                if not (c in forward_prev) or (dist_to_child < dist_so_far[c]):
                    forward_prev[c] = b
                    dist_so_far[c] = dist_to_child
                    heappush(frontier, (child_priority, c, target))
                    if not (c in boxes): boxes[c] = {}
                    boxes[c] = entry_point

            elif target == src:
                child_entry = get_detail_point(boxes[b], c)
                dist_to_child = dist_from_dst[b] + distance(boxes[b], child_entry)
                child_priority = dist_to_child + heuristic(child_entry, target)

                if not (c in backward_prev) or (dist_to_child < dist_from_dst[c]):
                    backward_prev[c] = b
                    dist_from_dst[c] = dist_to_child
                    heappush(frontier, (child_priority, c, target))
                    if not (c in boxes): boxes[c] = {}
                    boxes[c] = entry_point
    
    # ERROR HANDLING
    if not path:
        # if no valid path is found, the function prints an error message
        print("No path!")

        # and constructs a degenerate path consisting of the source and destination points
        path.append(src)
        path.append(dst)
        boxes[src_box] = True
        boxes[dst_box] = True
    
    # RETURN
    return path, boxes  # returns the final path and the boxes dictionary mapping boxes to detailed points