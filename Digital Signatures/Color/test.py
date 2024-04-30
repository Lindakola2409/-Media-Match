import numpy as np
from skimage import color
import time
import json
import copy

# f1 = open("data8Q.json")
f1 = open("data8Q(Alt)_large.json")
dataQ = json.load(f1)
# f2 = open("data8.json")
f2 = open("data8(Alt)_large.json")
dataOG = json.load(f2)
f1.close()
f2.close()

def normalize(val):
    for i in range(len(val)):
        for j in range(len(val[i])):
            val[i][j] = val[i][j]/255

### OG

# temp1 = [[39, 38, 85], [159, 170, 206], [48, 68, 144]]
# temp2 = [[65, 53, 126], [19, 28, 69], [150, 159, 189]]

# temp1 = [[47 , 57 , 113 ], [176 , 186 , 205 ], [109 , 122 , 160 ]]
# temp2 = [[161 , 172 , 189 ], [33 , 37 , 74 ], [91 , 99 , 132 ]]

# temp1 = [[43, 37, 80], [45, 67, 143], [161, 171, 205]]
# temp2 = [[21, 29, 69], [150, 159, 190], [60, 53, 133]]

### Alt

# temp1 = [[195 , 201 , 210 ], [194 , 200 , 209 ], [199 , 205 , 214 ]]
# temp2 = [[197 , 203 , 212 ], [184 , 190 , 199 ], [183 , 189 , 198 ]]

# temp1 = [[33, 65, 146], [32, 64, 145], [34, 66, 147]]
# temp2 = [[14, 31, 88], [6, 9, 27], [14, 35, 95]]

def color_similarity(color1, color2):
    temp1 = copy.deepcopy(color1)
    temp2 = copy.deepcopy(color2)
    normalize(temp1)
    normalize(temp2)
    temp3 = np.zeros((len(temp1), 3))
    temp4 = np.zeros((len(temp2), 3))

    for i in range(len(temp1)):
        temp1[i].reverse()
        temp3[i] = color.rgb2lab([[temp1[i]]])[0][0]
    for i in range(len(temp2)):
        temp2[i].reverse()
        temp4[i] = color.rgb2lab([[temp2[i]]])[0][0]

    return np.linalg.norm(temp3 - temp4)

def color_distance(color1, color2):
    temp1 = copy.deepcopy(color1)
    temp2 = copy.deepcopy(color2)
    normalize(temp1)
    normalize(temp2)

    temp3 = np.zeros((len(temp1), 3))
    temp4 = np.zeros((len(temp2), 3))
    distances = np.zeros((len(temp3), len(temp4)))

    for i in range(len(temp1)):
        temp1[i].reverse()
        temp3[i] = color.rgb2lab([[temp1[i]]])[0][0]
    for i in range(len(temp2)):
        temp2[i].reverse()
        temp4[i] = color.rgb2lab([[temp2[i]]])[0][0]

    for i in range(len(temp3)):
        for j in range(len(temp4)):
            distances[i, j] = np.linalg.norm(temp3[i] - temp4[j])

    min_distance_pairs = []
    used_rows = set()
    used_columns = set()
    for anchor in range(len(temp3)):
        min_distance = float("inf")
        min_row_index = -1
        min_column_index = -1
        for runner in range(len(temp4)):
            if runner not in used_columns:
                if distances[anchor, runner] < min_distance:
                    min_distance = distances[anchor, runner]
                    min_row_index = anchor
                    min_column_index = runner
            if runner not in used_rows:
                if anchor < len(temp4) and runner < len(temp3) and distances[runner, anchor] < min_distance:
                    min_distance = distances[runner, anchor]
                    min_row_index = runner
                    min_column_index = anchor
        min_distance_pairs.append((min_row_index, min_column_index))
        used_rows.add(min_row_index)
        used_columns.add(min_column_index)

    # find average distance
    average_distance = 0
    for i in range(len(min_distance_pairs)):
        average_distance += distances[min_distance_pairs[i][0], min_distance_pairs[i][1]]
    average_distance /= len(min_distance_pairs)

    return average_distance

# compare frame by frame color of dataQ with dataOG
threshold = 64 #17.2 for OG, 44 for Alt

# print(color_distance(temp1, temp2))
# input()

i = 15747
start = time.time()
while i < len(dataOG):
    valid = True
    print("Checking frame", i)
    for j in range(len(dataQ)):
        dist = color_distance(dataOG[str(i+j)], dataQ[str(j)])
        # print(dataQ)
        if dist > threshold:
            if i > 15746 and i < 15753:
                print("No match for frame", i, "and", j, "with distance", dist)
                # input()
            valid = False
            break
    if valid:
        print("Found match for frame", i)
        break
    i += 1
print("Time taken:", time.time() - start)

# i = 0
# start = time.time()
# while i < len(dataOG):
#     valid = True
#     print("Checking frame", i)
#     for j in range(len(dataQ)):
#         dist = color_similarity(dataOG[str(i+j)], dataQ[str(j)])
#         # print(dataQ)
#         if dist > threshold:
#             if i > 15749 and i < 15752:
#                 print("No match for frame", i, "and", j, "with distance", dist)
#                 input()
#             valid = False
#             break
#     if valid:
#         print("Found match for frame", i)
#         break
#     i += 1
# print("Time taken:", time.time() - start)
