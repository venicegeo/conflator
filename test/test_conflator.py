import os
import unittest
from conflator import Conflator
from conflator.utils import write_geojson, read_geojson_features


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    coast1 = os.path.join(testpath, 'shoreline1.geojson')
    coast2 = os.path.join(testpath, 'shoreline2.geojson')
    coast3 = os.path.join(testpath, 'shoreline3.geojson')

    def get_conflator(self):
        """ Get a conflator object """
        return Conflator(read_geojson_features(self.coast2), tolerance=0.001)

    def test_conflator_init_empty(self):
        """ Create conflation without reference lines """
        conflator = Conflator()
        self.assertEqual(len(conflator.matches), len(conflator.reference))
        self.assertEqual(len(conflator.reference), 0)

    def test_conflator_init(self):
        """ Create conflation with reference lines """
        conflator = self.get_conflator()
        self.assertEqual(len(conflator.matches), len(conflator.reference))
        self.assertEqual(len(conflator.reference), 2854)
        self.assertEqual(conflator.tolerance, 0.001)

    def test_conflator_save_load(self):
        conflator = self.get_conflator()
        fname = os.path.join(testpath, 'conflator_save_load.geojson')
        conflator.save(fname)
        conflator = Conflator.load(fname)
        self.assertEqual(len(conflator.matches), len(conflator.reference))
        self.assertEqual(len(conflator.reference), 2854)
        self.assertEqual(conflator.tolerance, 0.001)

    def test_conflator_conflate(self):
        """ Conflate two sets of lines """
        conflator = self.get_conflator()
        conflator.conflate(read_geojson_features(self.coast1))
        self.assertEqual(len(conflator.reference), 2854)

        write_geojson(conflator.get_reference(), os.path.join(testpath, 'conflate_ref.geojson'))
        write_geojson(conflator.get_matched(), os.path.join(testpath, 'conflate_matched.geojson'))
        write_geojson(conflator.get_diff(), os.path.join(testpath, 'conflate_diff.geojson'))
        write_geojson(conflator.get_conflation(thresh=1), os.path.join(testpath, 'conflate_conflation.geojson'))

    def test_conflator_3sets(self):
        """ Conflate three sets of lines """
        conflator = self.get_conflator()
        conflator.conflate(read_geojson_features(self.coast1))
        conflator.conflate(read_geojson_features(self.coast3))
        self.assertEqual(len(conflator.reference), 3475)

        write_geojson(conflator.get_reference(), os.path.join(testpath, 'conflate3_ref.geojson'))
        write_geojson(conflator.get_matched(), os.path.join(testpath, 'conflate3_matched.geojson'))
        write_geojson(conflator.get_diff(), os.path.join(testpath, 'conflate3_diff.geojson'))
        write_geojson(conflator.get_conflation(thresh=1), os.path.join(testpath, 'conflate3_conflation.geojson'))
