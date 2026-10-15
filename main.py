#!/usr/bin/env python3
"""
3D geodesic sphere: a hollow, open wireframe with an open middle using Open3D.

Every setting is read from a .env file (no values are hard-coded here).
The script looks for .env next to itself first, then in the working
directory, or you can point at one with --env.

Requires:  pip install numpy matplotlib open3d python-dotenv openpyxl
Usage:     python geodesic_sphere.py
           python geodesic_sphere.py --env path/to/other.env

Drag with the mouse to rotate manually, scroll to zoom.
"""

import argparse
import ctypes
import sys
from pathlib import Path
from importlib.metadata import version

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import open3d as o3d

from config import Config
from program_settings import ProgramSettings

# Mathematical constants of the icosahedron (geometry, not settings).
PHI = (1 + 5 ** 0.5) / 2

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


def load_config() -> Config:
    def get(key: str, cast):
        val = ProgramSettings.get_setting(key)
        if val is None:
            sys.exit(f"Error: missing required setting {key} in environment")
        try:
            return cast(val)
        except ValueError:
            sys.exit(f"Error: invalid value for {key}: {val!r}")

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
# Handy utility methods
# --------------------------------------------------------------------------

def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_package_version(pkg_name: str) -> str:
    return version(pkg_name)


def get_required_package_names() -> list[str]:
    packages: list[str] = []
    with open('requirements.txt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            package = line.split('~')[0].strip()
            packages.append(package)

    packages.sort(key=str.lower)
    return packages


def get_libusb_version() -> str:
    """Retrieve the native libusb version using ctypes."""
    try:
        # Determine the likely library path based on the operating system
        if sys.platform == "darwin":
            lib_paths = [
                "/opt/homebrew/opt/libusb/lib/libusb-1.0.0.dylib",
                "/usr/local/opt/libusb/lib/libusb-1.0.0.dylib",
                "libusb-1.0.dylib"
            ]
        elif sys.platform == "win32":
            lib_paths = ["libusb-1.0.dll"]
        else:
            lib_paths = ["libusb-1.0.so", "libusb-1.0.so.0"]

        libusb = None
        for path in lib_paths:
            try:
                libusb = ctypes.CDLL(path)
                break
            except OSError:
                continue

        if not libusb:
            return "libusb shared library not found"

        # Define the C structure returned by libusb_get_version()
        class LibUsbVersion(ctypes.Structure):
            _fields_ = [
                ("major", ctypes.c_uint16),
                ("minor", ctypes.c_uint16),
                ("micro", ctypes.c_uint16),
                ("nano", ctypes.c_uint16),
                ("rc", ctypes.c_char_p),
                ("describe", ctypes.c_char_p),
            ]

        libusb.libusb_get_version.restype = ctypes.POINTER(LibUsbVersion)
        v = libusb.libusb_get_version().contents

        # Build the version string
        version_str = f"{v.major}.{v.minor}.{v.micro}"
        if v.nano:
            version_str += f".{v.nano}"
        if v.rc:
            version_str += f"-{v.rc.decode('utf-8', errors='ignore')}"
        return version_str

        return f"{v.major}.{v.minor}.{v.micro}"
    except Exception as e:
        return f"Unavailable ({e})"

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    print(f'Python version: {get_python_version()}')

    package_names = get_required_package_names()
    for pkg in package_names:
        try:
            version_info = get_package_version(pkg)
            print(f"{pkg:<16}{version_info}")
        except Exception as e:
            print(e)

    print(f"{'libusb':<16}{get_libusb_version()}")

    parser = argparse.ArgumentParser(description="Hollow geodesic wireframe sphere using Open3D")
    parser.parse_args()

    cfg = load_config()

    tris = open_middle(geodesic_triangles(cfg.frequency), cfg.opening)
    edges = unique_edges(tris) * cfg.sphere_radius

    # Color each edge by its height using matplotlib colormap.
    z = edges[:, :, 2].mean(axis=1)
    colors = plt.get_cmap(cfg.colormap)((z - z.min()) / (np.ptp(z) or 1.0))[:, :3]

    # Prepare Open3D LineSet data
    # Create independent points for each segment to preserve individual segment colors
    num_edges = len(edges)
    points = edges.reshape(-1, 3)
    lines = np.array([[2 * i, 2 * i + 1] for i in range(num_edges)], dtype=np.int32)

    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector(colors)

    # Setup Open3D Visualizer window
    win_width = int(cfg.figure_size * 100)
    win_height = int(cfg.figure_size * 100)

    title_text = ""
    if cfg.show_title:
        title_text = (
            f"Geodesic wireframe  |  radius {cfg.sphere_radius:g}  |  "
            f"frequency {cfg.frequency}  |  {len(edges)} edges"
        )

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=title_text or "Geodesic Sphere", width=win_width, height=win_height)

    vis.add_geometry(line_set)

    # Set background color and line width
    opt = vis.get_render_option()
    bg_rgb = mcolors.to_rgb(cfg.background_color)
    opt.background_color = np.array(bg_rgb)
    opt.line_width = cfg.line_width

    # Handle spinning animation if requested
    if cfg.spin:
        def animation_callback(vis_obj):
            ctr = vis_obj.get_view_control()
            # Rotate view horizontally based on spin_speed
            ctr.rotate(cfg.spin_speed * 10.0, 0.0)
            return False

        vis.register_animation_callback(animation_callback)

    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    main()