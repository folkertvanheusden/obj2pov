This program convertes wavefront .obj-files to something that can be rendered by PovRay or OpenSCAD.
The first release is still rather limited altough the minecraft obj-files produced by https://github.com/jmc2obj/j-mc-2-obj work quite well.

Usage:

    ./obj2pov.py -f inputfile.obj > outputfile.pov

For OpenSCAD output:

    ./obj2pov.py -S -f inputfile.obj > outputfile.scad

Then you can render it with PovRay/OpenSCAD.
For PovRay you may want to tweak the camera location and maybe add some more lights.

Note that for a model from j-mc-2-obj, you want to tick 'Create a seperate object for each block' and untick 'Do not allow duplicate vertexes' in the export window.

Example render with PovRay : https://youtu.be/b0ljLMfLrgQ

These examples how a minecraft segment converted to OpenSCAD.
* https://vanheusden.com/permshare/minecraft.scad.xz  this one is large and takes ages to load
* https://vanheusden.com/permshare/minecraft2.scad.xz  smaller segment, renders in a few minutes
* https://vanheusden.com/permshare/minecraft2-scad.png  how it looks in OpenSCAD
* https://vanheusden.com/permshare/minecraft3-scad.png  larger segment but with occlude enabled in jmc2obj
* https://vanheusden.com/permshare/minecraft3.scad.xz  the generated OpenSCAD file




Released under the MIT license by

Folkert van Heusden <mail@vanheusden.com>
