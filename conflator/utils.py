import math
import json
from copy import deepcopy


def read_geojson(filename):
    with open(filename) as f:
        geojson = json.loads(f.read())
    return geojson


def read_geojson_features(filename):
    gj = read_geojson(filename)
    return [feat['geometry']['coordinates'] for feat in gj['features']]


def write_geojson(geojson, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(geojson))


def lines_to_segments(lines):
    """ Turn list of lines into list of segments """
    segments = []

    for line in lines:
        for i in range(len(line)-1, 0, -1):
            a = line[i-1]
            b = line[i]
            if (a[0] != b[0] or a[1] != b[1]):
                segments.append([a, b])
    return segments


def segments_to_lines(segments, snap=0.0):
    """ Turn list of segments into lines """
    lines = []
    if len(segments) == 0:
        return lines
    line = deepcopy(segments[0])
    for seg in segments[1:]:
        xdist = line[-1][0] - seg[0][0]
        ydist = line[-1][1] - seg[0][1]
        dist = math.sqrt(xdist * xdist + ydist * ydist)
        if dist <= snap:
            line.append(seg[1])
        else:
            line = deepcopy(seg)
            lines.append(line)
    lines.append(line)
    return lines


def segments_to_features(segments, snap=0.0, **kwargs):
    lines = segments_to_lines(segments, snap=snap)
    return lines_to_features(lines, **kwargs)


def lines_to_features(lines, properties=None, metadata=None):
    """ Create features from lines """
    features = []
    for gid, line in enumerate(lines):
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': line
            },
            'properties': {
                'id': gid
            }
        }
        if properties is not None:
            for key in properties:
                feature['properties'][key] = properties[key][gid]
        features.append(feature)
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    if metadata is not None:
        geojson['metadata'] = metadata
    return geojson
