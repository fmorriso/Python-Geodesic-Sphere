#!/usr/bin/env python3
"""
3D geodesic sphere: a hollow, open wireframe with an open middle.

Every setting is read from a .env file (no values are hard-coded here).
The script looks for .env next to itself first, then in the working
directory, or you can point at one with --env.

Requires:  pip install numpy matplotlib
Usage:     python geodesic_sphere.py
           python geodesic_sphere.py --env path/to/other.env

Drag with the mouse to rotate manually.
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from dotenv import dotenv_values
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from config import Config

# Mathematical constants of the icosahedron (geometry, not settings).
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

def find_env_file(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            sys.exit(f"Error: env file not found: {path}")
        return path
    for folder in (Path(__file__).resolve().parent, Path.cwd()):
        candidate = folder / ".env"
        if candidate.is_file():
            return candidate
    sys.exit("Error: no .env file found next to the script or in the working directory.")


def load_config(path: Path) -> Config:
    env = {k: v for k, v in dotenv_values(path).items() if v is not None}

    def get(key: str, cast):
        if key not in env:
            sys.exit(f"Error: missing required setting {key} in {path}")
        try:
            return cast(env[key])
        except ValueError:
            sys.exit(f"Error: invalid value for {key} in {path}: {env[key]!r}")

    def to_bool(text: str) -> bool:
        lowered = text.lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
        raise ValueError(text)

    cfg = Config(
        sphere_radius=get("SPHERE_RADIUS", float),
        frequency=get("FREQUENCY", int),
        opening=get("OPENING", float),
        line_width=get("LINE_WIDTH", float),
        colormap=get("COLORMAP", str),
        background_color=get("BACKGROUND_COLOR", str),
        title_color=get("TITLE_COLOR", str),
        figure_size=get("FIGURE_SIZE", float),
        show_title=get("SHOW_TITLE", to_bool),
        elevation=get("ELEVATION", float),
        start_azimuth=get("START_AZIMUTH", float),
        spin=get("SPIN", to_bool),
        spin_speed=get("SPIN_SPEED", float),
        frame_interval=get("FRAME_INTERVAL", int),
        frame_count=get("FRAME_COUNT", int),
    )

    if cfg.sphere_radius <= 0:
        sys.exit("Error: SPHERE_RADIUS must be greater than 0")
    if cfg.frequency < 1:
        sys.exit("Error: FREQUENCY must be at least 1")
    if cfg.colormap not in plt.colormaps():
        sys.exit(f"Error: unknown COLORMAP {cfg.colormap!r}")
    return cfg


# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
def normalize(p: np.ndarray) -> np.ndarray:
    return p / np.linalg.norm(p)


def geodesic_triangles(frequency: int) -> np.ndarray:
    """Return an (N, 3, 3) array of triangles on the unit sphere."""
    n = frequency
    tris: list[np.ndarray] = []

    for ia, ib, ic in ICO_FACES:
        a, b, c = ICO_VERTS[ia], ICO_VERTS[ib], ICO_VERTS[ic]
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
    if opening <= 0:
        return tris
    centres_z = tris[:, :, 2].mean(axis=1)
    return tris[np.abs(centres_z) >= opening]


def unique_edges(tris: np.ndarray) -> np.ndarray:
    """Turn triangles into a de-duplicated (E, 2, 3) array of line segments."""
    seen: set[tuple] = set()
    edges: list[np.ndarray] = []
    for tri in tris:
        for k in range(3):
            p, q = tri[k], tri[(k + 1) % 3]
            key = tuple(sorted((tuple(np.round(p, 6)), tuple(np.round(q, 6)))))
            if key not in seen:
                seen.add(key)
                edges.append(np.array([p, q]))
    return np.array(edges)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Hollow geodesic wireframe sphere")
    parser.add_argument("--env", help="path to a .env file (default: auto-detect)")
    cfg = load_config(find_env_file(parser.parse_args().env))

    tris = open_middle(geodesic_triangles(cfg.frequency), cfg.opening)
    edges = unique_edges(tris) * cfg.sphere_radius

    # Colour each edge by its height.
    z = edges[:, :, 2].mean(axis=1)
    colors = plt.get_cmap(cfg.colormap)((z - z.min()) / (np.ptp(z) or 1.0))

    fig = plt.figure(
        figsize=(cfg.figure_size, cfg.figure_size), facecolor=cfg.background_color
    )
    ax = fig.add_subplot(projection="3d", facecolor=cfg.background_color)

    wire = Line3DCollection(edges, colors=colors, linewidths=cfg.line_width)
    ax.add_collection3d(wire)

    lim = cfg.sphere_radius * 1.05
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=cfg.elevation, azim=cfg.start_azimuth)

    if cfg.show_title:
        fig.suptitle(
            f"Geodesic wireframe  |  radius {cfg.sphere_radius:g}  |  "
            f"frequency {cfg.frequency}  |  {len(edges)} edges",
            color=cfg.title_color,
        )

    if cfg.spin:
        def spin(frame: int):
            ax.view_init(
                elev=cfg.elevation, azim=cfg.start_azimuth + frame * cfg.spin_speed
            )
            return (wire,)

        _anim = FuncAnimation(
            fig, spin, frames=cfg.frame_count, interval=cfg.frame_interval, blit=False
        )

    plt.show()


if __name__ == "__main__":
    main()