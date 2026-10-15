import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def create_icosahedron():
    """Generates the starting vertices and faces of an icosahedron."""
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio

    # 12 initial vertices
    vertices = [
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ]

    # Normalize vertices to sit on a unit sphere
    vertices = np.array(vertices, dtype=float)
    vertices /= np.linalg.norm(vertices[0])

    # 20 triangular faces
    faces = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ]
    return vertices.tolist(), faces


def get_midpoint(v1_idx, v2_idx, cache, vertices):
    """Finds or creates a midpoint between two vertices, normalized to the sphere surface."""
    # Use a sorted tuple as the key so the edge (v1, v2) is the same as (v2, v1)
    key = tuple(sorted([v1_idx, v2_idx]))
    if key in cache:
        return cache[key]

    # Calculate midpoint
    p1 = np.array(vertices[v1_idx])
    p2 = np.array(vertices[v2_idx])
    mid = (p1 + p2) / 2

    # Normalize the new point so it gets pushed out to the spherical shell
    mid /= np.linalg.norm(mid)

    vertices.append(mid.tolist())
    new_index = len(vertices) - 1
    cache[key] = new_index
    return new_index


def subdivide(vertices, faces):
    """Subdivides each triangle into 4 smaller triangles."""
    cache = {}
    new_faces = []

    for face in faces:
        v1, v2, v3 = face

        # Get the midpoints of the three edges
        a = get_midpoint(v1, v2, cache, vertices)
        b = get_midpoint(v2, v3, cache, vertices)
        c = get_midpoint(v3, v1, cache, vertices)

        # Form 4 new triangles from the original vertices and the midpoints
        new_faces.extend([
            [v1, a, c],
            [v2, b, a],
            [v3, c, b],
            [a, b, c]
        ])

    return vertices, new_faces


def build_geodesic_sphere(subdivisions=2, radius=1.0):
    """Builds the geodesic sphere with the specified complexity and radius."""
    vertices, faces = create_icosahedron()

    for _ in range(subdivisions):
        vertices, faces = subdivide(vertices, faces)

    # Scale to the configured radius
    vertices = np.array(vertices) * radius
    return vertices, np.array(faces)


def plot_wireframe(vertices, faces, radius):
    """Renders the 3D wireframe using matplotlib."""
    fig = plt.figure(figsize=(8, 8))
    fig.patch.set_facecolor('#111111')  # Dark background
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#111111')

    # Create the 3D polygon collection using the vertices organized by faces
    mesh = Poly3DCollection(
        vertices[faces],
        facecolors='none',  # Transparent faces for wireframe effect
        edgecolors='cyan',  # Wireframe color
        linewidths=0.5,
        alpha=0.8
    )
    ax.add_collection3d(mesh)

    # Configure axes limits to ensure the sphere isn't distorted
    ax.set_xlim([-radius, radius])
    ax.set_ylim([-radius, radius])
    ax.set_zlim([-radius, radius])

    # Remove axis lines and grid for a clean wireframe look
    ax.set_axis_off()

    # Set the aspect ratio equal to prevent egg-shaping
    ax.set_box_aspect([1, 1, 1])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Increase subdivisions for a smoother, more complex sphere (e.g., 1 to 5)
    # Be careful going above 5, as the geometry complexity increases exponentially!
    CONFIG_SUBDIVISIONS = 3

    # The physical unit radius of the sphere
    CONFIG_RADIUS = 5.0
    # ---------------------

    print(f"Generating Geodesic Sphere (Radius: {CONFIG_RADIUS}, Subdivisions: {CONFIG_SUBDIVISIONS})...")
    verts, tris = build_geodesic_sphere(subdivisions=CONFIG_SUBDIVISIONS, radius=CONFIG_RADIUS)

    print(f"Total Vertices: {len(verts)}")
    print(f"Total Faces: {len(tris)}")

    plot_wireframe(verts, tris, radius=CONFIG_RADIUS)