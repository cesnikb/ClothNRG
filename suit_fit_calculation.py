import numpy as np
import math,os,sys


def get_area_of_triangle(l):
    a = l[0]
    b = l[1]
    c = l[2]
    ab1 = float(b[0]) - float(a[0])
    ab2 = float(b[1]) - float(a[1])
    ab3 = float(b[2]) - float(a[2])
    ac1 = float(c[0]) - float(a[0])
    ac2 = float(c[1]) - float(a[1])
    ac3 = float(c[2]) - float(a[2])

    AB = np.array([ab1,ab2,ab3])
    AC = np.array([ac1,ac2,ac3])
    c = np.cross(AB,AC)

    c_mag = math.sqrt(math.pow(c[0],2) + math.pow(c[1],2) + math.pow(c[2],2))

    return c_mag/2

def import_obj_files(file_path):
    f = open(file_path, "r")

    obj_data = dict()
    obj_data["v"] = []
    obj_data["f"] = []

    for x in f:
        value = x.strip().split(" ")
        if value[0] == "v":
            obj_data["v"].append([value[1], value[2], value[3]])
        if value[0] == "f":
            obj_data["f"].append([value[1], value[2], value[3]])
    return obj_data

def save_to_vertex():
    pass

def normalize_vertex(x, max, min):
    return (x - min) / (max - min)


cloth_obj_last = import_obj_files("/home/cesnik/nrg_cloth_simulator/simulatedData/00020_00.obj")
cloth_obj_first = import_obj_files("/home/cesnik/nrg_cloth_simulator/simulatedData/00000_00.obj")
vertex_changes = [[] for i in range(len(cloth_obj_first["v"]))]

for face in cloth_obj_first["f"]:
    v1 = int(face[0].split("/")[0])
    v2 = int(face[1].split("/")[0])
    v3 = int(face[2].split("/")[0])
    first = cloth_obj_first["v"][v1-1],cloth_obj_first["v"][v2-1],cloth_obj_first["v"][v3-1]
    last = cloth_obj_last["v"][v1-1],cloth_obj_last["v"][v2-1],cloth_obj_last["v"][v3-1]

    plane_size_first = get_area_of_triangle(first)
    plane_size_last = get_area_of_triangle(last)
    vertex_changes[v1-1].append(plane_size_first-plane_size_last)
    vertex_changes[v2-1].append(plane_size_first-plane_size_last)
    vertex_changes[v3-1].append(plane_size_first-plane_size_last)

for i,v in enumerate(vertex_changes):
    vertex_changes[i] = sum(vertex_changes[i])/len(vertex_changes)

# print(vertex_changes)
max_v = max(sorted(vertex_changes)[int(len(vertex_changes)*0.01):-int(len(vertex_changes)*0.01)])
min_v = min(sorted(vertex_changes)[int(len(vertex_changes)*0.01):-int(len(vertex_changes)*0.01)])
f_out = open(os.path.join(sys.argv[1],"vertex_value.txt"), "w")

for i,v in enumerate(vertex_changes):
    vertex_changes[i] = normalize_vertex(v,max_v,min_v)
    if vertex_changes[i] < 0:
        out_text = 0
    elif vertex_changes[i] > 1:
        out_text = 1
    else:
        out_text = vertex_changes[i]
    f_out.write(str(out_text)+"\n")
f_out.close()
#print(sorted(vertex_changes))
# print(get_area_of_triangle([[0.098131, 0.0335933,0.310724],[0.0884455,0.0273689,0.314843],[0.0893312, 0.0257522, 0.315317]]))

