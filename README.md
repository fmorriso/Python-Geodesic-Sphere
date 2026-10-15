# Python Geodesic Sphere

Python - 3D Geodesic Sphere

## Tools Used

| Tool          | Version |
|:--------------|--------:|
| Python        |  3.14.7 |
| libusb        |  1.0.30 |
| matplotlib    |  3.11.2 |
| numpy         |   2.5.4 |
| open3d        |  0.20.0 |
| openpyxl      |   3.1.5 |
| python-dotenv |   1.2.4 |

## Change History (newest on top)

| Date       | Description      |
|:-----------|:-----------------|
| 2026-10-15 | Initial creation |

## Developers - PLEASE READ

* Requires Python 3.14 or newer. I developed the code originally using python 3.14.7.
* Requires ```libusb```, which is **NOT** a python package, but must be installed separately to support ```open3d``` which **IS** a python package.
On a MacBook running macOS 27.0.1, I installed it via the following command in a Terminal session:
```commandline
brew install libusb
```

To make this program work, after bringing down the code from GitHub,
you must make a new file called **_.env_** in the same directory as `main.py` that holds
the configuration values used to control the size and shape of the sphere.

Here's an example:

```text
# Geodesic sphere settings
# Every value used by main.py and config.py comes from this file.

# --- Geometry ---
# Radius of the sphere (number > 0)
SPHERE_RADIUS=1.0
# Mesh density: 1 = bare icosahedron, higher = finer wireframe (integer >= 1)
FREQUENCY=3
# Half-height of the open band around the equator (0 = closed, ~0.9 = nearly all removed)
OPENING=0

# --- Appearance ---
LINE_WIDTH=1.4
# Any matplotlib colormap name (cool, viridis, plasma, turbo, ...)
COLORMAP=cool
BACKGROUND_COLOR=#0b0f1a
TITLE_COLOR=white
FIGURE_SIZE=8
SHOW_TITLE=true

# --- View / animation ---
ELEVATION=20
START_AZIMUTH=30
# Auto-rotate the view (true/false)
SPIN=true
# Degrees of rotation per frame
SPIN_SPEED=0.8
# Milliseconds between frames
FRAME_INTERVAL=30
# Frames before the animation loops
FRAME_COUNT=450
```

## References
### Prerequisites & Documentation
This project uses **Open3D** for rendering the 3D geodesic wireframe. 
* For installation instructions and quick-start tutorials, see the [Open3D Getting Started Guide](https://www.open3d.org/docs/latest/getting_started.html).
* For deeper class and function details, explore the [Open3D Python API Reference](https://www.open3d.org/docs/latest/python_api/open3d.html).

### Geometry Theory References
* **[Regular Icosahedron Geometry on Wikipedia](https://en.wikipedia.org/wiki/Regular_icosahedron):** Covers the
  fundamental Platonic solid underlying all geodesic spheres, including Cartesian coordinates using the golden ratio
  ($\phi \approx 1.618$) and symmetry properties.
* **[Geodesic Domes Mathematics by Tom Davis](http://www.geometer.org/mathcircles/geodesic.pdf):** A comprehensive
  mathematical paper explaining the geometry of spherical projection, edge subdivision frequencies, and vertex
  configuration.
* **[Geodesic Math and Structural Layouts by Jay Salsburg](https://www.salsburg.com/geod/geodesicmath.pdf):** Detailed
  notes on analytical geometry, great-circle grids, and chord calculations required to map flat planar polygons onto a
  spherical shell.
* **[A geodesic sphere is formed by subdividing an icosahedron](https://www.youtube.com/shorts/sE2CP3R4-JI):** YouTube video