PyOSMExtract
============

A program to take an area exported from the OpenStreetMap website and extract interesting information to a JSON representation.

Currently, this extracts:
* Neighbourhoods
* Waterways
* Parks
* Cemeteries

Usage
-----

1. Go to [https://www.openstreetmap.org/](https://www.openstreetmap.org/)
2. Use the `Export` function to obtain the .osm file
3. Set the filename at the bottom of the `parse_osm.py` file
4. Create an `ignore_regions.txt` file with one entry per line of regions to ignore
5. Run `python parse_osm.py`
6. The output JSON is found in the same directory as the input .osm file