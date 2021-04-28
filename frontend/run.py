import argparse
from typing import NoReturn

from dashboard import create_app


def main(args: argparse.Namespace) -> NoReturn:
    if args.debug == 'True':
        debug = True
    elif args.debug == 'False':
        debug = False
    else:
        raise ValueError('Unknown value for "debug". Only "True" and "False" are possible')

    config = args.config
    app = create_app(config, debug)
    app.run(host=args.host, port=args.port, debug=debug)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        required=False,
        default='False',
        help=(
            'If True, the application will use a WSGI server. '
            'If False, it will be run on default Flask server in a debug mode.'
        ),
    )
    parser.add_argument('--config', type=str, required=False, default='', help='A dotenv file path.')
    parser.add_argument(
        '--host', type=str, required=False, default='localhost', help='A host where server is deployed.'
    )
    parser.add_argument('--port', type=int, required=False, default=8050, help='A port where server is deployed.')
    args = parser.parse_args()
    main(args)
