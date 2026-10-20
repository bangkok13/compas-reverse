"""Small original binary STL used only in the visibly marked demo project."""
import math
import struct


def gear_stl():
    triangles = []
    segments = 96
    for i in range(segments):
        j = (i + 1) % segments
        def point(index, radius, z):
            angle = index * 2 * math.pi / segments
            return (math.cos(angle) * radius, math.sin(angle) * radius, z)
        outer_i = 30 if i % 4 in (1, 2) else 26
        outer_j = 30 if j % 4 in (1, 2) else 26
        a, b = point(i, outer_i, 0), point(j, outer_j, 0)
        c, d = point(i, outer_i, 8), point(j, outer_j, 8)
        e, f = point(i, 10, 0), point(j, 10, 0)
        g, h = point(i, 10, 8), point(j, 10, 8)
        triangles.extend([(a, b, d), (a, d, c), (c, d, h), (c, h, g),
                          (a, f, b), (a, e, f), (e, g, h), (e, h, f)])
    output = b"Demonstration gear - not a manufactured part".ljust(80, b"\0") + struct.pack("<I", len(triangles))
    for triangle in triangles:
        output += struct.pack("<12fH", 0, 0, 0, *(coordinate for point in triangle for coordinate in point), 0)
    return output
