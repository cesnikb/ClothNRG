from genson import SchemaBuilder
import os
import sys
# {
#     "frame_time": 0.04,
#     "frame_steps": 8,
#     "end_time": 10,
#     "cloths": [{
#         "mesh": "meshes/square4_sub.obj",
#         //"transform": {"translate": [-0.5, -1, 0.5]},
#          "transform": {"translate": [0.5, 0, 0.5]},
#         "materials": [{"data": "materials/gray-interlock.json",
#                        "thicken": 2}],
#         "remeshing": {
#             "refine_angle": 0.3,
#             "refine_compression": 0.005,
#             "refine_velocity": 0.5,
#             "size": [10e-3, 200e-3],
#             "aspect_min": 0.2
#         }
#     }],
#     "handles": [{"nodes": [1,3], "end_time": 7}],
#     "motions": [[
#         {"time": 0, "transform": {"scale": 0.1, "translate": [0,0,0]}},
#         {"time": 1, "transform": {"scale": 0.1, "translate": [0,0,0]}},
#         {"time": 2, "transform": {"scale": 0.1, "translate": [0,0,0]}},
#         {"time": 3, "transform": {"scale": 0.1, "translate": [0,-1.5,0]}},
#         {"time": 4, "transform": {"scale": 0.1, "translate": [0,0,0]}},
#         {"time": 5, "transform": {"scale": 0.1, "translate": [0,1.5,0]}},
#         {"time": 6, "transform": {"scale": 0.1, "translate": [0,0,0]}},
#         {"time": 7, "transform": {"scale": 0.1, "translate": [0,-0.4,0]}}
#     ]],
#     "obstacles": [{
#         "mesh": "meshes/sphere.obj",
#         "motion": 0
#     }],
#     "gravity": [0, 0, -9.8],
#     "disable": ["popfilter", "remeshing" ],
#     "magic": {"repulsion_thickness": 5e-3, "collision_stiffness": 1e6}
# }


def main():
    print(str(sys.argv))

    mesh = sys.argv[2]
    dataLocation = os.path.join(sys.argv[1],sys.argv[3])
    material = os.path.join(sys.argv[1],"materials/"+sys.argv[4])

    builder = SchemaBuilder()
    builder.add_schema({
        "frame_time": 0.04,
        "frame_steps": 4,
        "end_time": 1,
        "cloths": [{
            "mesh": mesh,

            "materials": [{"data": material,
                           "thicken": 2}],
            "remeshing": {
                "refine_angle": 0.3,
                "refine_compression": 0.005,
                "refine_velocity": 0.5,
                "size": [10e-3, 200e-3],
                "aspect_min": 0.2
            }
        }],
        "handles": [{"end_time": 7}],
        "motions": [[
            {"time": 0, "transform": {"scale": 1.0},}
        ]],
        "obstacles": [{
            "mesh": dataLocation+"/body.obj",
            "motion": 0
        }],
        "gravity": [0, 0, -9.8],
        "disable": ["popfilter", "remeshing"],
        "magic": {"repulsion_thickness": 5e-3, "collision_stiffness": 1e6}
    })

    builder.to_schema()
    file = open(os.path.join(str(dataLocation), 'conf.json'), 'w')
    file.write(builder.to_json(indent=1))
    file.close()

if __name__ == "__main__":
    main()