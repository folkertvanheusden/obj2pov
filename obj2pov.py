#! /usr/bin/python3

# (C) 2023-2024 by Folkert van Heusden

import getopt
import hashlib
import math
import numpy
import os
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
        usemtl = None
        self.mtl = dict()

        path = os.path.dirname(obj_file)
        fh = open(obj_file, 'r')

        error_seen = set()

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

                    error_seen.add(parts[0])

        fh.close()

        if mtl_file == None:
            return

        mtl_name = None
        mtl_file = (path + '/' if path != '' else '') + mtl_file

        print(f'Loading mtl-file from {mtl_file}', file=sys.stderr)

        fh = open(mtl_file, 'r')

        for line in fh.readlines():
            if line[0] == '#':
                continue

            parts = line.split()

            if len(parts) == 0:
                continue

            if parts[0] == 'newmtl':
                mtl_name = parts[1]
                self.mtl[mtl_name] = dict()

            elif parts[0] == 'Kd':
                self.mtl[mtl_name]['color'] = [float(f) for f in parts[1:]]

            elif parts[0] == 'map_Kd':
                self.mtl[mtl_name]['texture'] = parts[1]

        fh.close()

    def get_faces_povray(self):
        meshes = []
        for face_element in w.face_element_list:
            mesh = []

            for indices in face_element[0]:
                mesh.append(self.vertexes[indices.vertex_index - 1])

            meshes.append((mesh, face_element[1]))

        return meshes

    def get_openscad(self):
        polyhedrons = []

        for face_element in w.face_element_list:
            polyhedron = dict()
            polyhedron['vertices'] = dict()
            polyhedron['faces'] = []
            polyhedron['texture'] = face_element[1]
            nr = 0
            for indices in face_element[0]:
                if indices.vertex_index - 1 not in polyhedron['vertices']:
                    polyhedron['vertices'][indices.vertex_index - 1] = (nr, self.vertexes[indices.vertex_index - 1])
                    nr += 1
                cur_nr = polyhedron['vertices'][indices.vertex_index - 1]
                polyhedron['faces'].append(cur_nr[0])

            polyhedrons.append(polyhedron)

        return polyhedrons

    def get_mtl_color(self, name, gen_if_missing = True):
        if name in self.mtl:
            return self.mtl[name]['color']

        if gen_if_missing:
            face_name_hash = hashlib.sha256(face[1].encode('utf-8')).digest()

            r = face_name_hash[0] / 255
            g = face_name_hash[1] / 255
            b = face_name_hash[2] / 255

            return (r, g, b)

        return (None, None, None)

    def get_mtl_texture(self, name):
        if name in self.mtl:
            return self.mtl[name]['texture']

        return None

m = dict()

def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        if i[0] == 0 and i[1] == 0 and i[2] == 0 and i[3] == 0:  # hack for exported minecraft
            continue
        curr_frequency = List.count(i)
        if curr_frequency > counter:
            counter = curr_frequency
            num = i

    return num

# from https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv
def determine_color_of_file(file):
    try:
        if file in m:
            return m[file]

        print(f'Processing {file}', file=sys.stderr)

        import cv2, numpy as np
        from sklearn.cluster import KMeans

        image = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        reshape = image.reshape((image.shape[0] * image.shape[1], 4))

        # Find and display most dominant colors
        cluster = KMeans(n_clusters=100).fit(reshape)
        #print(cluster.cluster_centers_, cluster.inertia_, file=sys.stderr)
        #print(most_frequent(cluster.cluster_centers_.tolist()), file=sys.stderr)

#        if 'leaves' in file:
#            print(cluster.cluster_centers_, file=sys.stderr)

        mf = most_frequent(cluster.cluster_centers_.tolist())
        r, g, b, a = mf[0] / 255, mf[1] / 255, mf[2] / 255, mf[3] / 255
        m[file] = (r, g, b, a)

        return r, g, b, a

    except Exception as e:
        print(e, file=sys.stderr)
        return 1, 1, 1, 1

def help():
    print('-f x  file to process')
    print('-S    openscad output instead of povray')
    print('-t    use most dominant color from texture instead of file reference')
    print('-h    this help')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'f:Sth')
except getopt.GetoptError as err:
    print(err)
    help()
    sys.exit(2)

file = None
png_color = False
povray = True

for o, a in opts:
    if o == '-f':
        file = a
    elif o == '-t':
        png_color = True
    elif o == '-S':
        povray = False
    elif o == '-h':
        help()
        sys.exit(0)

if file == None:
    help()
    sys.exit(1)

print(f'Processing {file}...', file=sys.stderr)
w = wavefront(file)

if povray:
    avg_center = [0., 0., 0.]
    sd_center = [0., 0., 0.]

    faces = w.get_faces_povray()

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

        texture = w.get_mtl_texture(face[1])

        if not texture is None:
            dot = texture.rfind('.')
            if dot == -1:
                ext = 'png'
            else:
                ext = texture[dot + 1:].lower()

            if png_color:
                r, g, b, a = determine_color_of_file(texture)
                print('  texture { pigment { color rgbt <%f, %f, %f, %f> } }' % (r, g, b, 1.0 - a))

            else:
                # crude plane detection
                sdx = numpy.std([f[0] for f in face[0]])
                sdy = numpy.std([f[1] for f in face[0]])
                sdz = numpy.std([f[2] for f in face[0]])

                if sdx < sdy and sdx < sdz:
                    rot = 'rotate <0, 90, 0>'
                elif sdy < sdx and sdy < sdz:
                    rot = 'rotate <90, 0, 0>'
                else:
                    rot = 'rotate <0, 0, 90>'

                print('  texture { pigment { image_map { %s "%s" } %s } }' % (ext, texture, rot))

        else:
            r = 0.4
            g = 1.0
            b = 0.4

            if not face[1] is None:
                r, g, b = w.get_mtl_color(face[1])

            print('  texture { pigment { color rgb <%f, %f, %f> } }' % (r, g, b))

        print('}')

    # camera
    camera_distance_mul = 3

    print('camera {')
    print(f'  look_at<{avg_center[0]}, {avg_center[1]}, {avg_center[2]}>')
    print(f'  location<{avg_center[0] + sd_center[0] * camera_distance_mul}, {avg_center[1] + sd_center[1] * camera_distance_mul}, {avg_center[2] + sd_center[2] * camera_distance_mul}>')
    print(f'  right x * image_width / image_height')
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
                print('  color rgb <0.5, 0.5, 0.5>')
                print('}')

else:
    import collections
    for polyhedron in w.get_openscad():
        if polyhedron['texture'] != None:
            texture = w.get_mtl_texture(polyhedron['texture'])
            r, g, b, a = determine_color_of_file(texture)
            print(f'color([{r},{g},{b},{a}]) ')
        print('polyhedron(')
        l = [point[1] for point in [polyhedron['vertices'][v] for v in polyhedron['vertices']]]
        print(f'points={l},')
        f = [point[0] for point in [polyhedron['vertices'][v] for v in polyhedron['vertices']]]
        print(f'faces=[{f}]')
        print(');')
