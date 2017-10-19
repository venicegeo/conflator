import os
import logging
import numpy
from rtree import index
from .segment import match_segment
from .utils import read_geojson, read_geojson_features, write_geojson, \
    lines_to_segments, lines_to_features, segments_to_lines


logger = logging.getLogger(__name__)


_TOLERANCE = 0.001


class Conflator(object):
    """ Conflate multiple linestring vectors """

    def __init__(self, reflines=[], tolerance=_TOLERANCE):
        self.reference = lines_to_segments(reflines)[::-1]
        self.tolerance = tolerance
        self.matches = [0] * len(self.reference)
        self.matched = []
        self.diff = []

    def conflate(self, lines):
        """ Add new lines to the conflation object """
        if self.diff is not None:
            # add the previous difference to reference
            self.reference = self.reference + self.diff
            self.matches += [0] * len(self.diff)
        self.match_segments(lines_to_segments(lines))

    def conflate_geojsons(self, geojsons):
        """ Conflate all of these """
        for gj in geojsons:
            logger.info('Adding %s' % os.path.basename(gj))
            self.conflate(read_geojson_features(gj))

    def get_reference(self):
        """ Get reference as lines """
        return lines_to_features(segments_to_lines(self.reference))

    def get_matched(self):
        """ Get matched lines """
        return lines_to_features(segments_to_lines(self.matched))

    def get_diff(self):
        """ Get vectors different from reference """
        return lines_to_features(segments_to_lines(self.diff))

    def get_conflation(self, matched=0, snap=0, minlen=3):
        """ Get conflated vectors with optional 'match' tolerance """
        segs, matches = self.get_conflated_segments()
        if matched > 0:
            inds = numpy.where(numpy.array(matches) >= matched)
            segs = [segs[i] for i in inds[0]]
        lines = segments_to_lines(segs, snap=snap)
        lines = filter(lambda x: len(x) >= minlen, lines)
        return lines_to_features(lines)

    def get_conflated_segments(self):
        """ Get coordinates and # of matches for all segments (ref + diff) """
        if self.diff is None:
            return self.reference, self.matches
        segs = self.reference + self.diff
        matches = self.matches + [0] * len(self.diff)
        return segs, matches

    def save(self, filename):
        """ Save conflated segments as GeoJSON """
        segs, matches = self.get_conflated_segments()
        geojson = lines_to_features(segs, metadata={'tolerance': self.tolerance}, properties={'matches': matches})
        write_geojson(geojson, filename)

    @classmethod
    def load(cls, filename):
        """ Load conflated segments from GeoJSON """
        geojson = read_geojson(filename)
        segments = [feat['geometry']['coordinates'] for feat in geojson['features']]
        tolerance = geojson['metadata']['tolerance']
        conflate = Conflator(tolerance=tolerance)
        conflate.reference = segments
        conflate.matches = [feat['properties']['matches'] for feat in geojson['features']]
        return conflate

    def get_index(self):
        """ Generate spatial index for reference segments """
        assert(len(self.matches) == len(self.reference))
        idx = index.Index()
        for i, segment in enumerate(self.reference):
            idx.insert(i, self.segment_bbox(segment), obj={'matches': self.matches[i], 'seg': segment})
        return idx

    def match_segments(self, segments):
        """ Match collection of segments against reference """
        self.matched = []
        self.diff = []
        tree = self.get_index()
        while len(segments):
            seg = segments.pop()
            close_segments = tree.intersection(self.segment_bbox(seg), objects=True)
            match = False
            # loop through close segments. unmatched parts of segment added to segments queue
            for close_seg in close_segments:
                if (match_segment(seg, close_seg.object['seg'], self.tolerance, segments)):
                    match = True
                    break
            if match:
                self.matches[close_seg.id] += 1
                self.matched.append(seg)
            else:
                self.diff.append(seg)

    def segment_bbox(self, segment):
        """ Get bbox of this segment """
        a = segment[0]
        b = segment[1]
        return [
            min(a[0], b[0]) - self.tolerance,  # minX
            min(a[1], b[1]) - self.tolerance,  # minY
            max(a[0], b[0]) + self.tolerance,  # maxX
            max(a[1], b[1]) + self.tolerance   # maxY
        ]
