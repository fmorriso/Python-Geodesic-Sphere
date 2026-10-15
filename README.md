# Python Geodesic Sphere

Python - 3D Geodesic Sphere

## Tools Used

| Tool            | Version |
|:----------------|--------:|
| Python          |  3.14.7 |
| VSCode          | 1.141.0 |
| matplotlib           |  3.11.2 |
| numpy |  2.5.4 |
| python-dotenv   |   1.2.4 |

## Change History (newest on top)

| Date       | Description                            |
|:-----------|:---------------------------------------|
| 2026-09-23 | use built-in type instead of TypeAlias |
| 2026-06-16 | Move html to separate file             |
| 2026-06-15 | Initial creation                       |

## Developers - PLEASE READ

Requires Python 3.12 or newer

To make this program work, after bringing down the code from GitHub,
you must make a new file called **_.env_** in the same directory as `src/main.py` that holds the file system path to where
the map coordinates are located.

Here's an example:

```text
COORDINATES_FILE = "bounding_box.json"
```

### PyQt6 quirk to watch out for

Make sure the two PyQt6 packages have compatible versions using:

```bash
python3 -m pip install --user --upgrade --force-reinstall PyQt6 PyQt6-WebEngine
```

## References

For more information on how to map your data, check out
the [Folium Documentation](https://python-visualization.github.io/folium/latest/).
