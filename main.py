"""Parse a file with logs."""

import argparse

AVERAGE_REPORT_NAME = 'average'


def get_command_line_options() -> argparse.Namespace:
    """Return command line options."""
    parser = argparse.ArgumentParser(description='Log file parser.')
    parser.add_argument(
        '-f', '--file', type=str, nargs='+', required=True, help='File to parse (possibly multiple values).'
    )
    parser.add_argument(
        '-r',
        '--report',
        type=str,
        choices=[
            AVERAGE_REPORT_NAME,
        ],
        default=AVERAGE_REPORT_NAME,
        help=f'Type report (default: {AVERAGE_REPORT_NAME}).',
    )
    args = parser.parse_args()
    return args


def main():
    """Execute the script step by step."""
    _ = get_command_line_options()
    pass


if __name__ == '__main__':
    main()
