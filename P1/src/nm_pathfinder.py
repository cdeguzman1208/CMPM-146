# imports
from heapq import heappop, heappush     # heap queue functions: pop, push
from math import inf, pow, sqrt         # math functions: infinity, power, square root

# find_path()
def find_path(source_point, destination_point, mesh):   # function definition
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
    path = []   # path list
    boxes = {}  # boxes dictionary
    
    # SUGGESTED WORKFLOW
    # identify the source and destination boxes
    source_box = find_box(source_point, mesh)               # source box
    destination_box = find_box(destination_point, mesh)     # destination box

    # scan through the list of boxes to find which tontains the source point
    priority_box = source_box
    if (source_box is None or destination_box is None):
        print("No path!")
        path.append(source_point)
        path.append(destination_point)

        if (source_box is not None):
            boxes[source_box] = True
        if (destination_box is not None):
            boxes[destination_box] = True
        return path, boxes.keys()   # instead of returning a list indicating  that you haven't visited any boxes
    
    # do this as well for the destination point
    if (source_point == destination_point):
        path.append(source_point)
        path.append(destination_point)
        boxes[source_box] = True
        boxes[destination_box] = True
        return path, boxes.keys()   # return a list of these two boxes

    boxes[source_box] = True
    priority_source = source_point
    entrypoint = None
    frontier = []  # takes in a (priority, {stuff})

    # stuff has:
    # current box
    # destination type (source or destination) to distinguish forward or back
    heappush(frontier, (-1, source_box, destination_point))
    heappush(frontier, (-1, destination_box, source_point))

    # detail points
    forward_points = {source_box : source_point}
    backward_points = {destination_box : destination_point}

    # used to track edge costs
    forward_cost = {source_box: 0}
    backward_cost = {destination_box: 0}

    # track backpointers
    forward_prev = {source_box : None}
    backward_prev = {destination_box : None}

    pathFound = False
    while (frontier):
        priority_priority, priority_box, curr_goal = heappop(frontier)
        boxes[priority_box] = True

        # Check if goal box has been explored by other search direction
        if ((curr_goal == destination_point and priority_box in backward_prev)
            or (curr_goal == source_point and priority_box in forward_prev)):
            pathFound = True
            break

        points, prev, cost_so_far, goal_box = (forward_points, forward_prev, forward_cost, destination_box) \
                                                if (curr_goal == destination_point) else \
                                                (backward_points, backward_prev, backward_cost, source_box)
        priority_source = points[priority_box]

        for neighbor in mesh["adj"][priority_box]:
            entrypoint = find_next_point(priority_source, priority_box, neighbor)
            link_cost = euclidean(priority_source, entrypoint)
            new_cost = cost_so_far[priority_box] + link_cost

            # if (neighbor == goal_box):
            #     new_cost += euclidean(entrypoint, curr_goal)

            if (neighbor not in prev or new_cost < cost_so_far[neighbor]):
                cost_so_far[neighbor] = new_cost
                prev[neighbor] = priority_box
                points[neighbor] = entrypoint

                # We must handle when we arrive at the destination box
                # This is because the cost from the entry to the goal point matters.
                # But there is the argument
                # if (neighbor != goal_box):
                #     priority_priority = new_cost + euclidean(entrypoint, curr_goal)
                # else:
                #     priority_priority = new_cost

                priority_priority = new_cost + euclidean(entrypoint, curr_goal)
                heappush(frontier, (priority_priority, neighbor, curr_goal))

    if (pathFound):
        # print("Found Path")
        # assert(forward_points[source_box] == source_point)
        # assert(backward_points[destination_box] == destination_point)
        # assert(len(path) == len(set(path)))
        forward_path = construct_path(priority_box, source_box, forward_prev, forward_points)
        backward_path = construct_path(priority_box, destination_box, backward_prev, backward_points, None, False)

        # handle any cases where we have duplicate when stitching paths together
        if (len(forward_path) > 0 and len(backward_path) > 0):
            if (forward_path[-1] == backward_path[0]):
                forward_path = forward_path[:-1]

        path = forward_path + backward_path
        print(backward_path)

    else:
        path.append(source_point)
        path.append(destination_point)
        boxes[source_box] = True
        boxes[destination_box] = True
        print("No path!")

    return path, boxes.keys()

def path_length(path):
    ret = 0
    pathlength = len(path)
    if (pathlength > 2):
        for i in range(1, pathlength):
            ret += euclidean(path[i - 1], path[i])
    return ret

def construct_path(last_box, target_box, prev_dict, points_dict, last_point=None, reverse=True):
    """
    Constructs a path from the given box_point to the target_box using the prev_dict.

    Args:
        last_box: The current box and point tuple (box, point)
        target_box: The target box to reach
        prev_dict: Dictionary containing the back pointers of each box
        points_dict: Dictionary mapping boxes to the points they contain
        last_point: the point in last_box (destination point)

    Returns:
        The constructed path as a list of points from box_point to target_box
    """
    path = []
    curr_box = last_box

    # Initialize with a point first...
    if (last_point is not None):
        path.append(last_point)
    else:
        if (curr_box != target_box):
            path.append(points_dict[curr_box])
            curr_box = prev_dict[curr_box]

    while curr_box != target_box:
        if (path[-1] != points_dict[curr_box]): # remove duplicates
            path.append(points_dict[curr_box])
        curr_box = prev_dict[curr_box] # (290, 625) (108, 525)

    if (len(path) == 0 or (len(path) > 0 and path[-1] != points_dict[target_box])):
        path.append(points_dict[target_box])

    if (reverse):
        path.reverse()

    return path

def find_box(p, mesh):
    for box in mesh["boxes"]:
        if (check_in_box(p, box)):
            return box
    return None

def check_in_box(p, box):
    return (box[0] <= p[0] <= box[1]) and (box[2] <= p[1] <= box[3])

def euclidean(p1=(0, 0), p2=(0, 0)):
    # Euclidean Hueistic
    return sqrt(pow((p2[1] - p1[1]), 2) + pow((p2[0] - p1[0]), 2))

# p is the current point

def find_next_point(n, sourcebox, destinationbox):
    ret_x = n[0]
    ret_y = n[1]

    # check if left and right meet
    if (sourcebox[0] == destinationbox[1] or sourcebox[1] == destinationbox[0]):
        ret_x = sourcebox[0] if (sourcebox[0] == destinationbox[1]) else sourcebox[1]

        # y range (max of the top, the min of the bottom)
        top = max(sourcebox[2], destinationbox[2])  # b1y1 , b2y1
        bottom = min(sourcebox[3], destinationbox[3])  # b1y2 , b2y2
        ret_y = top if (n[1] <= top) else bottom if (bottom <= n[1]) else n[1]

    # check if top and down meet
    if (sourcebox[2] == destinationbox[3] or sourcebox[3] == destinationbox[2]):
        ret_y = sourcebox[2] if (sourcebox[2] == destinationbox[3]) else sourcebox[3]

        # x range (Max of the left, the min of the right)
        left = max(sourcebox[0], destinationbox[0])  # b1x1 , b2x1
        right = min(sourcebox[1], destinationbox[1])  # b1x2 , b2x2
        ret_x = left if (n[0] <= left) else right if (right <= n[0]) else n[0]

    return (ret_x, ret_y)

def astar_find_path(source_point, destination_point, mesh):
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
    # mapping of boxes to (backpointer to previous box), used to find the path
    boxes = {}
    # p is the current from the source
    # q will be the current from the
    source_box = find_box(source_point, mesh)
    destination_box = find_box(destination_point, mesh)

    priority_box = source_box
    q_box = destination_box

    if (source_box is None or destination_box is None):
        print("No path!")
        path.append(source_point)
        path.append(destination_point)
        if (source_box is not None):
            boxes[source_box] = True
        if (destination_box is not None):
            boxes[destination_box] = True
        return path, boxes.keys()

    boxes[source_box] = True
    priority_source = source_point
    entrypoint = None
    frontier = []  # takes in a (priority, {stuff})

    # stuff has:
    # current box

    heappush(frontier, (0, priority_box))
    forward_points = {source_box : source_point}

    # used to track edge costs
    forward_cost = {source_box: 0}

    # track backpointers
    forward_prev = {}
    backward_prev = {}

    forward_prev[priority_box] = None
    backward_prev[q_box] = None

    pathFound = False
    while (frontier):
        priority_priority, priority_box = heappop(frontier)
        boxes[priority_box] = True

        if (priority_box == destination_box):
            pathFound = True
            break

        priority_source = forward_points[priority_box]
        for neighbor in mesh["adj"][priority_box]:

            entrypoint = find_next_point(priority_source, priority_box, neighbor)
            link_cost = euclidean(priority_source, entrypoint)
            new_cost = forward_cost[priority_box] + link_cost

            # if (neighbor == destination_box):
            #     new_cost += euclidean(entrypoint, destination_point)

            if (neighbor not in forward_prev or new_cost < forward_cost[neighbor]):
                forward_cost[neighbor] = new_cost
                forward_prev[neighbor] = priority_box
                forward_points[neighbor] = entrypoint

                # if (neighbor != destination_box):
                #     priority_priority = new_cost + euclidean(entrypoint, destination_point)
                # else:
                #     priority_priority = new_cost

                priority_priority = new_cost + euclidean(entrypoint, destination_point)

                heappush(frontier, (priority_priority, neighbor))

    if (pathFound):
        # assert(forward_points[source_box] == source_point)
        path = construct_path(priority_box, source_box, forward_prev, forward_points, destination_point)

    else:
        path.append(source_point)
        path.append(destination_point)
        boxes[source_box] = True
        boxes[destination_box] = True
        print("No path!")

    return path, boxes.keys()