This program convertes wavefront .obj-files to something that can be rendered by povray or openscad.
The first release is still rather limited altough the minecraft obj-files produced by https://github.com/jmc2obj/j-mc-2-obj work quite well.

Usage:

    ./obj2pov.py -f inputfile.obj > outputfile.pov

For openscad output:

    ./obj2pov.py -S -f inputfile.obj > outputfile.scad

Then you can render it with povray/openscad altough you may want to tweak the camera location and maybe add some more lights.
Example render: https://youtu.be/b0ljLMfLrgQ

Note that for a model from j-mc-2-obj, you want to tick 'Create a seperate object for each block' and untick 'Do not allow duplicate vertexes' in the export window.


Released under the MIT license by

Folkert van Heusden <mail@vanheusden.com>
