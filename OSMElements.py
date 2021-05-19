class OSMNode:

    def __init__(self, ident, lat, lon):
        self.ident = ident
        self.lat = float(lat)
        self.lon = float(lon)
        self.tags = {}

    def __repr__(self):
        return f"Node {self.ident}: {self.lat} {self.lon} {self.tags}"

    def to_json(self):
        ret = {'ident': self.ident, 'lat': self.lat, 'lon': self.lon}
        if self.tags: ret['tags'] = self.tags
        return ret


class OSMWay:

    def __init__(self, ident):
        self.ident = ident
        self.nd = []
        self.tags = {}

    def __repr__(self):
        return f"Way {self.ident}: {self.nd} {self.tags}"

    def to_json(self):
        ret = {'ident': self.ident, 'nd': self.nd}
        if self.tags: ret['tags'] = self.tags
        return ret


class OSMRelation:

    def __init__(self, ident):
        self.ident = ident
        self.way_members = []
        self.node_members = []
        self.tags = {}

    def __repr__(self):
        return f"Relation {self.ident}: {self.way_members} {self.node_members} {self.tags}"

    def to_json(self):
        ret = {'ident': self.ident,
               'way_members': self.way_members,
               'node_members': self.node_members}
        if self.tags: ret['tags'] = self.tags
        return ret
