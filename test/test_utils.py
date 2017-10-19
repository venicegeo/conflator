import os
import unittest
import json
from conflator import Conflator
import conflator.linematch as linematch


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    coast1 = os.path.join(testpath, 'shoreline1.geojson')
    coast2 = os.path.join(testpath, 'shoreline2.geojson')
    coast3 = os.path.join(testpath, 'shoreline3.geojson')

    def read_geojson_as_lines(self, filename):
        with open(filename) as f:
            geojson = json.loads(f.read())
        return [feat['geometry']['coordinates'] for feat in geojson['features']]

    def write_geojson(self, geojson, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(geojson))

    def test_lines_to_segments(self):
        """ Convert lines into segments """
        lines = self.read_geojson_as_lines(self.coast1)
        self.assertEqual(len(lines), 11)
        segments = linematch.lines_to_segments(lines)
        self.assertEqual(len(segments), 926)

    def test_index_lines(self):
        """ Create rtree index of lines """
        lines = self.read_geojson_as_lines(self.coast1)
        segments = linematch.lines_to_segments(lines)
        index = linematch.index_segments(segments)
