#! /usr/bin/python3

import getopt
import hashlib
import math
import sys

class wavefront_indices:
    def __init__(self, vertex_index, texture_coordinate_index, normal_index):
        self.vertex_index = vertex_index
        self.texture_coordinate_index = texture_coordinate_index
        self.normal_index = normal_index

    def __repr__(self):
        return f'{self.vertex_index}/{self.texture_coordinate_index if not self.texture_coordinate_index is None else "-"}/{self.normal_index if not self.normal_index is None else "-"}'

class wavefront:
    def __init__(self, obj_file):
        self.vertexes = []

        self.face_element_list = []

        mtl_file = None

        fh = open(obj_file, 'r')

        error_seen = []

        usemtl = None

        for line in fh.readlines():
            if line[0] == '#':
                continue

            parts = line.split()

            if len(parts) == 0:
                continue

            if parts[0] == 'v':
                self.vertexes.append([float(s) for s in parts[1:]])

            elif parts[0] == 'mtllib':
                mtl_file = parts[1]

            elif parts[0] == 'usemtl':
                usemtl = parts[1]

            elif parts[0] == 'f':
                face_elements = []

                for element in parts[1:]:
                    element_parts = element.split('/')

                    vertex_index = int(element_parts[0]) if len(element_parts) >= 1 else None
                    texture_coordinate_index = int(element_parts[1]) if len(element_parts) >= 2 else None
                    normal_index = int(element_parts[2]) if len(element_parts) >= 3 else None

                    face_elements.append(wavefront_indices(vertex_index, texture_coordinate_index, normal_index))

                self.face_element_list.append((face_elements, usemtl))

            else:
                if not parts[0] in error_seen:
                    print(line, file=sys.stderr)

                    error_seen.append(parts[0])

        fh.close()

        if mtl_file == None:
            return

        self.mtl = dict()

        mtl_name = None

        fh = open(mtl_file, 'r')

        for line in fh.readlines():
            if line[0] == '#':
                continue

            parts = line.split()

            if len(parts) == 0:
                continue

            if parts[0] == 'newmtl':
                mtl_name = parts[1]

            elif parts[0] == 'Kd':
                self.mtl[mtl_name] = [float(f) for f in parts[1:]]

        fh.close()

    def get_faces(self):
        meshes = []
        for face_element in w.face_element_list:
            mesh = []

            for indices in face_element[0]:
                mesh.append(self.vertexes[indices.vertex_index - 1])

            meshes.append((mesh, face_element[1]))

        return meshes

    def get_mtl_color(self, name):
        if name in self.mtl:
            return self.mtl[name]

        face_name_hash = hashlib.sha256(face[1].encode('utf-8')).digest()

        r = face_name_hash[0] / 255
        g = face_name_hash[1] / 255
        b = face_name_hash[2] / 255

        return (r, g, b)

w = wavefront(sys.argv[1])

avg_center = [0., 0., 0.]
sd_center = [0., 0., 0.]

faces = w.get_faces()

# determine center
div_count = 0
for face in faces:
    for f in face[0]:
        for i in range(0, 3):
            avg_center[i] += f[i]

            sd_center[i] += f[i] * f[i]

    div_count += len(face[0])

# determine size of object
for i in range(0, 3):
    avg_center[i] /= div_count

    sd_center[i] = math.sqrt((sd_center[i] / div_count) - math.pow(avg_center[i], 2.0))

# emit objects
for face in faces:
    face[0].append(face[0][0])  # close polygonb

    print('polygon {')
    print(f'\t{len(face[0])},')
    print(','.join([f'<{f[0]}, {f[1]}, {f[2]}>' for f in face[0]]))

    r = 0.4
    g = 1.0
    b = 0.4

    if not face[1] is None:
        r, g, b = w.get_mtl_color(face[1])

    print('  texture { pigment { color rgb <%f, %f, %f> } }' % (r, g, b))

    print('}')

# camera
camera_distance_mul = 5

print('camera {')
print(f'  look_at<{avg_center[0]}, {avg_center[1]}, {avg_center[2]}>')
print(f'  location<{avg_center[0] + sd_center[0] * camera_distance_mul}, {avg_center[1] + sd_center[1] * camera_distance_mul}, {avg_center[2] + sd_center[2] * camera_distance_mul}>')
print('}')

# light sources
light_distance_mul = 5

for z in range(-1, 2):
    for y in range(-1, 2):
        for x in range(-1, 2):
            if x == 0 and y == 0 and z == 0:
                continue

            print('light_source {')
            print(f'  <{avg_center[0] + sd_center[0] * light_distance_mul * x}, {avg_center[1] + sd_center[1] * light_distance_mul * y}, {avg_center[2] + sd_center[2] * light_distance_mul * z}>')
            print('  color rgb <1.0, 1.0, 1.0>')
            print('}')
