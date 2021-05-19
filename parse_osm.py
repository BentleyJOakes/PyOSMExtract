import json
import xml.etree.ElementTree as ET

from OSMElements import OSMNode, OSMWay, OSMRelation
from osm_util import osm_calc_scale
from maps.progress import ProgressBar


class OSMParser:

    def __init__(self):
        self.fcn_dict = {
            'bounds': self.handle_bounds,
            'node': self.handle_node,
            'way': self.handle_way,
            'relation': self.handle_relation,
        }

        self.bounds = {}
        self.scale = {}

        self.m_per_degree_lat = None
        self.m_per_degree_lon = None

        self.nodes = {}
        self.ways = {}
        self.relations = {}

        self.ways_to_find = []
        self.nodes_to_find = []

        # relation names to ignore
        self.ignore_relations = []

    def handle_bounds(self, ele):
        print("Setting bounds: " + str(ele.attrib))
        self.bounds['minlat'] = float(ele.attrib['minlat'])
        self.bounds['minlon'] = float(ele.attrib['minlon'])
        self.bounds['maxlat'] = float(ele.attrib['maxlat'])
        self.bounds['maxlon'] = float(ele.attrib['maxlon'])

        m_per_degree_lat, m_per_degree_lon = osm_calc_scale(self.bounds['minlat'])
        self.scale['m_per_degree_lat'] = m_per_degree_lat
        self.scale['m_per_degree_lon'] = m_per_degree_lon

    def handle_node(self, ele):
        n = OSMNode(ele.attrib['id'], ele.attrib['lat'], ele.attrib['lon'])
        for child in ele:
            k = child.attrib['k']
            v = child.attrib['v']
            n.tags[k] = v
        self.nodes[n.ident] = n

    def handle_way(self, ele):
        w = OSMWay(ele.attrib['id'])

        for child in ele:
            if child.tag == "nd":
                ref = child.attrib['ref']
                w.nd.append(ref)
            elif child.tag == "tag":
                k = child.attrib['k']
                v = child.attrib['v']
                w.tags[k] = v

        is_canal = "water" in w.tags and w.tags["water"] == "canal"
        is_lake = "water" in w.tags and w.tags["water"] == "lake"
        is_park = "leisure" in w.tags and w.tags["leisure"] == "park"
        is_pond = "water" in w.tags and w.tags["water"] == "pond"
        if is_canal or is_lake or is_park or is_pond or ele.attrib['id'] in self.ways_to_find:
            self.ways[w.ident] = w

    def handle_relation(self, ele):
        r = OSMRelation(ele.attrib['id'])
        for child in ele:
            if child.tag == "member":
                ref = child.attrib['ref']
                if child.attrib['type'] == "way":
                    r.way_members.append((ref, child.attrib['role']))
                elif child.attrib['type'] == "node":
                    r.node_members.append((ref, child.attrib['role']))
            elif child.tag == "tag":
                k = child.attrib['k']
                v = child.attrib['v']
                r.tags[k] = v

                if k == "name" and v in self.ignore_relations:
                    return

        is_admin = "boundary" in r.tags and r.tags["boundary"] == "administrative"
        is_cemetary = "landuse" in r.tags and r.tags["landuse"] == "cemetary"
        is_river = "water" in r.tags and r.tags["water"] == "river"
        is_woods = "natural" in r.tags and r.tags["natural"] == "wood"
        if is_admin or is_cemetary or is_river or is_woods:
            self.relations[r.ident] = r

    def read_xml(self, filename):
        print("Reading file: " + filename)
        i = 0

        line_count = sum(1 for line in open(filename))
        print("Line count: " + str(line_count))

        print("Finding bounds")
        for i, context in enumerate(ET.iterparse(filename)):
            (event, elem) = context
            if elem.tag == "bounds":
                self.handle_bounds(elem)
                break

        print("Finding relations")
        relation_progress = ProgressBar(num_items=line_count)
        for i, context in enumerate(ET.iterparse(filename)):
            # (event, elem) = context
            if context[1].tag == "relation":
                self.handle_relation(context[1])
            relation_progress.update_progress(i)

        for r in self.relations.values():
            self.ways_to_find += [way[0] for way in r.way_members]
            self.nodes_to_find += [node[0] for node in r.node_members]

        print(f"\nFinding {len(self.ways_to_find)} ways...")
        ways_progress = ProgressBar(num_items=len(self.ways_to_find))
        i = 0
        for context in ET.iterparse(filename):
            # (event, elem) = context
            if context[1].tag == "way":
                self.handle_way(context[1])
                ways_progress.update_progress(i)
                i += 1

        for w in self.ways.values():
            self.nodes_to_find += w.nd

        print(f"\nFinding {len(self.nodes_to_find)} nodes...")
        nodes_progress = ProgressBar(num_items=len(self.nodes_to_find))
        i = 0
        for context in ET.iterparse(filename):
            # (event, elem) = context
            if context[1].tag == "node" and context[1].attrib['id'] in self.nodes_to_find:
                self.handle_node(context[1])
                nodes_progress.update_progress(i)
                i += 1

        # for n in self.nodes.values():
        #     print(n)

    def write_json(self, filename):
        print("Writing to file: " + filename)
        data = {
            'bounds': self.bounds,
            'scale': self.scale,
            'nodes': self.serialize_json(self.nodes),
            'ways': self.serialize_json(self.ways),
            'relations': self.serialize_json(self.relations),
        }

        with open(filename, 'w') as f:
            json.dump(data, f)  # , indent=4)

        print("File writing complete.")

    @staticmethod
    def serialize_json(d):
        new_dict = {}
        for k, v in d.items():
            new_dict[k] = v.to_json()
        return new_dict

    def load_ignore_relations(self, ignore_relations_filename):
        with open(ignore_relations_filename) as f:
            for line in f:
                self.ignore_relations.append(line)

if __name__ == "__main__":
    osmp = OSMParser()
    in_filename = "maps/river.osm"
    out_filename = in_filename + ".json"

    osmp.load_ignore_relations("ignore_regions.txt")

    osmp.read_xml(in_filename)

    osmp.write_json(out_filename)
