import json
import matplotlib.pyplot as plt
import numpy as np
import random

# Create a list of connections between keypoints to form the skeleton
connections = [
    (0, 1), (1, 2), (1, 5), (1, 8),         # Torso
    (8, 9), (8, 12),                        # Hips
    (2, 3), (3, 4),                         # Right Arm
    (5, 6), (6, 7),                         # Left Arm
    (9, 10), (10, 11),                      # Right Leg
    (12, 13), (13, 14),                     # Left Leg
    (0, 15), (15, 17), (0, 16), (16, 18),   # Face
    (14, 21), (14, 19), (19, 20),           # Left Foot
    (11, 24), (11, 22), (22, 23)            # Right Foot
]

face = [0, 15, 16, 17, 18]
r_foot = [11, 22, 23, 24]
l_foot = [14, 19, 20, 21]
hips = [8, 9, 12]


# # Load OpenPose JSON output
# with open(".\\output_videos_jsons\\insane\\insane_000000000800_keypoints.json", "r") as json_file:
#     data = json.load(json_file)

# # Assuming there's only one person in the frame
# keypoints = data['people'][0]["pose_keypoints_2d"]

# # Extract x and y coordinates and confidence values
# x_coords = keypoints[0::3]
# y_coords = keypoints[1::3]
# c_vals = keypoints[2::3]

# # Plot skeleton
# plt.scatter(x_coords, y_coords, c="red")  # Plot keypoints

# for connection in connections:
#     p1, p2 = connection
#     if (c_vals[p1] != 0 and c_vals[p2] != 0):
#         plt.plot([x_coords[connection[0]], x_coords[connection[1]]],
#                 [y_coords[connection[0]], y_coords[connection[1]]], c="blue")  # Connect keypoints

# plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
# plt.axis("equal")

# # show plot
# plt.show()


for frame in range(100, 800, 50):
    # Load OpenPose JSON output
    with open(".\\output_videos_jsons\\insane\\insane_000000000" + str(frame) +"_keypoints.json", "r") as json_file:
        data = json.load(json_file)

    # Assuming there's only one person in the frame
    keypoints = data['people'][0]["pose_keypoints_2d"]

    # Extract x and y coordinates and confidence values
    x_coords = keypoints[0::3]
    y_coords = keypoints[1::3]
    c_vals = keypoints[2::3]


    '''
    Test Mutate
    '''
    mutation_offset = 0.05
    mutated = []
    for i in range(25):
        if (c_vals[i] != 0 and i not in mutated):
            x_offset = (random.random() * 2 * mutation_offset) - mutation_offset
            y_offset = (random.random() * 2 * mutation_offset) - mutation_offset

            if (i in face):
                for j in face:
                    x_coords[j] += x_offset
                    y_coords[j] += y_offset
                    mutated.append(j)
            elif (i in r_foot):
                for j in r_foot:
                    x_coords[j] += x_offset
                    y_coords[j] += y_offset
                    mutated.append(j)
            elif (i in l_foot):
                for j in l_foot:
                    x_coords[j] += x_offset
                    y_coords[j] += y_offset
                    mutated.append(j)
            elif (i in hips):
                for j in hips:
                    x_coords[j] += x_offset
                    y_coords[j] += y_offset
                    mutated.append(j)
            else:
                x_coords[i] += x_offset
                y_coords[i] += y_offset
                mutated.append(j)



    # Plot skeleton
    plt.scatter(x_coords, y_coords, c="red")  # Plot keypoints

    for connection in connections:
        p1, p2 = connection
        if (c_vals[p1] != 0 and c_vals[p2] != 0):
            plt.plot([x_coords[connection[0]], x_coords[connection[1]]],
                    [y_coords[connection[0]], y_coords[connection[1]]], c="blue")  # Connect keypoints

    
    
    # plt.axis("equal")
    plt.ylim(0,0.85)
    plt.xlim(0,2)
    plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
    
    

    # Save plot as png
    fname = ".\\output_plot\\insane_mutated_v2\\frame_" + str(frame) + ".png"
    plt.savefig(fname)
    plt.clf()


# Finish Message
print("Done")