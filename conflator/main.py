import sys
import argparse
import logging
import json
from conflator import Conflator, _TOLERANCE
from .version import __version__
from .utils import read_geojson_features


logger = logging.getLogger(__name__)


def parse_args(args):
    desc = 'Conflator (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    parser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
    parser.add_argument('--log', default=1, type=int,
                        help='0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical')

    group = parser.add_argument_group('files')
    group.add_argument('geojson', nargs='*', help='List of GeoJSON files')
    group.add_argument('--fout', help='Conflated output', default='conflated.geojson')
    group.add_argument('--save', help='Filename to save conflated segments to', default=None)
    group.add_argument('--load', help='Filename of conflated segments for reference', default=None)

    group = parser.add_argument_group('conflation parameters')
    group.add_argument('--tol', help='Tolerance for conflation', default=_TOLERANCE, type=float)
    group.add_argument('--snap', help='Snapping distance between line endpoints', default=_TOLERANCE*2, type=float)
    group.add_argument('--matched', help='Minimum number of matches required to keep segment', default=0, type=int)
    group.add_argument('--minlen', help='Minimum length of lines to keep', default=3, type=int)


    # turn Namespace into dictinary
    parsed_args = vars(parser.parse_args(args))

    return parsed_args


def cli():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(stream=sys.stdout, level=args.pop('log') * 10)

    fnames = args.pop('geojson')

    if args['load']:
        conflator = Conflator.load(args['load'])
    else:
        if len(fnames) < 2:
            raise Exception("At least two GeoJSON arguments required")
        conflator = Conflator(read_geojson_features(fnames[0]), tolerance=args['tol'])
        fnames = fnames[1:]

    conflator.conflate_geojsons(fnames)

    if args['save'] is not None:
        conflator.save(args['save'])

    with open(args['fout'], 'w') as f:
        f.write(json.dumps(conflator.get_conflation(matched=args['matched'], snap=args['snap'], minlen=args['minlen'])))


if __name__ == "__main__":
    cli()
