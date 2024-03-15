import json
import os

directory = 'output_videos_jsons\\insane'

# frame = 100

# with open(".\\output_videos_jsons\\insane\\insane_000000000" + str(frame) +"_keypoints.json", "r") as json_file:
#     data = json.load(json_file)

dance_poses = []

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    print(f)

    with open(f, 'r') as json_file:
        pose_data = json.load(json_file)

    print(pose_data)
    dance_poses.append(pose_data)

print(dance_poses)