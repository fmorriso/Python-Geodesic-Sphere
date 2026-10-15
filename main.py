#!/usr/bin/env python3
"""
3D geodesic sphere with an open middle.

A subdivided icosahedron (icosphere) is projected onto a sphere, then every
triangle whose centre lies within a band around the equator is removed, so you
can see straight through the middle into the hollow interior.

Requires:  pip install numpy matplotlib
Usage:     python geodesic_sphere.py [--frequency 3] [--opening 0.35] [--no-spin]

Drag with the mouse to rotate manually.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

PHI = (1 + 5**0.5) / 2

ICO_VERTS = np.array(
    [
        (-1, PHI, 0), (1, PHI, 0), (-1, -PHI, 0), (1, -PHI, 0),
        (0, -1, PHI), (0, 1, PHI), (0, -1, -PHI), (0, 1, -PHI),
        (PHI, 0, -1), (PHI, 0, 1), (-PHI, 0, -1), (-PHI, 0, 1),
    ],
    dtype=float,
)
ICO_VERTS /= np.linalg.norm(ICO_VERTS, axis=1, keepdims=True)

ICO_FACES = [
    (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
    (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
    (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
    (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
]


def normalize(p: np.ndarray) -> np.ndarray:
    return p / np.linalg.norm(p)


def geodesic_triangles(frequency: int) -> np.ndarray:
    """Return an (N, 3, 3) array of triangles on the unit sphere."""
    n = frequency
    tris: list[np.ndarray] = []

    for ia, ib, ic in ICO_FACES:
        a, b, c = ICO_VERTS[ia], ICO_VERTS[ib], ICO_VERTS[ic]

        # Grid of points across the flat face, pushed out onto the sphere.
        pts = {
            (i, j): normalize(a + (b - a) * i / n + (c - a) * j / n)
            for i in range(n + 1)
            for j in range(n + 1 - i)
        }

        for i in range(n):
            for j in range(n - i):
                tris.append(np.array([pts[i, j], pts[i + 1, j], pts[i, j + 1]]))
                if i + j <= n - 2:
                    tris.append(
                        np.array([pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]])
                    )

    return np.array(tris)


def open_middle(tris: np.ndarray, opening: float) -> np.ndarray:
    """Remove triangles whose centre is within |z| < opening of the equator."""
    centres_z = tris[:, :, 2].mean(axis=1)
    return tris[np.abs(centres_z) >= opening]


def main() -> None:
    parser = argparse.ArgumentParser(description="Geodesic sphere with an open middle")
    parser.add_argument("-f", "--frequency", type=int, default=3,
                        help="subdivision frequency (higher = finer mesh), default 3")
    parser.add_argument("-o", "--opening", type=float, default=0.35,
                        help="half-height of the open band, 0 to 1, default 0.35")
    parser.add_argument("--no-spin", action="store_true", help="disable auto-rotation")
    args = parser.parse_args()

    tris = open_middle(geodesic_triangles(args.frequency), args.opening)

    # Colour each face by its height for a nice gradient.
    z = tris[:, :, 2].mean(axis=1)
    colors = plt.cm.viridis((z - z.min()) / (np.ptp(z) or 1.0))
    colors[:, 3] = 0.85

    fig = plt.figure(figsize=(8, 8), facecolor="#0b0f1a")
    ax = fig.add_subplot(projection="3d", facecolor="#0b0f1a")

    mesh = Poly3DCollection(tris, facecolors=colors, edgecolors="white", linewidths=0.6)
    ax.add_collection3d(mesh)

    lim = 1.0
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=20, azim=30)
    fig.suptitle(
        f"Geodesic sphere  |  frequency {args.frequency}  |  {len(tris)} faces",
        color="white",
    )

    if not args.no_spin:
        def spin(frame: int):
            ax.view_init(elev=20, azim=30 + frame * 0.8)
            return (mesh,)

        # Keep a reference so the animation isn't garbage collected.
        _anim = FuncAnimation(fig, spin, frames=450, interval=30, blit=False)

    plt.show()


if __name__ == "__main__":
    main()