from stl import mesh
import numpy as np

# Cylinder parameters
radius_bottom = 2.6
radius_top = 2.0
height = 20.0
gap = 15.0
segments = 32
num_cylinders = 3
base_thickness = 1.0

# Total plate size
total_width = num_cylinders*2*radius_bottom + (num_cylinders-1)*gap + radius_bottom  # add margin for cylinder diameter
total_depth = 2*radius_bottom*2 + radius_bottom  # add margin for cylinder diameter

def make_tapered_cylinder(r_bottom, r_top, height, segments):
    vertices = []
    faces = []
    for i in range(segments):
        theta = 2*np.pi*i/segments
        x_b, y_b = r_bottom*np.cos(theta), r_bottom*np.sin(theta)
        x_t, y_t = r_top*np.cos(theta), r_top*np.sin(theta)
        vertices.append([x_b, y_b, 0])
        vertices.append([x_t, y_t, height])
    vertices = np.array(vertices)

    # Side faces
    for i in range(segments):
        i0 = 2*i
        i1 = 2*((i+1)%segments)
        i2 = i0+1
        i3 = i1+1
        faces.append([i0,i1,i2])
        faces.append([i2,i1,i3])

    # Top/bottom center vertices
    bottom_center_idx = len(vertices)
    top_center_idx = len(vertices)+1
    vertices = np.vstack([vertices, [0,0,0],[0,0,height]])

    # Top/bottom faces
    for i in range(segments):
        i0 = 2*i
        i1 = 2*((i+1)%segments)
        i2 = i0+1
        i3 = i1+1
        faces.append([i0,i1,bottom_center_idx])
        faces.append([i3,i2,top_center_idx])

    return vertices, np.array(faces)

def make_base_plate(width, depth, thickness):
    vertices = np.array([
        [0,0,0],[width,0,0],[width,depth,0],[0,depth,0],
        [0,0,thickness],[width,0,thickness],[width,depth,thickness],[0,depth,thickness]
    ])
    faces = np.array([
        [0,1,4],[1,5,4],[1,2,5],[2,6,5],
        [2,3,6],[3,7,6],[3,0,7],[0,4,7],
        [4,5,7],[5,6,7],[0,1,3],[1,2,3]
    ])
    return vertices, faces

def translate(vertices, offset):
    return vertices + np.array(offset)


#===== Build objects ===== 

all_vertices = []
all_faces = []
vertex_offset = 0

# Base plate
base_v, base_f = make_base_plate(total_width, total_depth, base_thickness)
all_vertices.append(base_v)
all_faces.append(base_f + vertex_offset)
vertex_offset += len(base_v)

# Create cylinders
for i in range(num_cylinders):
    v, f = make_tapered_cylinder(radius_bottom, radius_top, height, segments)

    # Effective row width of all cylinders + gaps
    cyl_row_width = num_cylinders*2*radius_bottom + (num_cylinders-1)*gap

    # Centering offset in X
    margin_x = (total_width - cyl_row_width) / 2

    # X offset: place cylinders along the plate
    offset_x = i*(2*radius_bottom + gap) + radius_bottom + margin_x
    # Y offset: center cylinders along Y
    offset_y = total_depth/2
    # Z offset: on top of plate
    offset_z = base_thickness

    v = translate(v, [offset_x, offset_y, offset_z])

    all_vertices.append(v)
    all_faces.append(f + vertex_offset)
    vertex_offset += len(v)

# Combine
vertices = np.vstack(all_vertices)
faces = np.vstack(all_faces)

# Create mesh
m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    m.vectors[i] = vertices[f]

m.save('PETG_Stringing_Test.stl')
print("STL saved as PETG_Stringing_Test.stl")
