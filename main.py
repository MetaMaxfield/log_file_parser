"""Parse a file with logs."""

import argparse
import json

from endpoint_stats import EndpointStats

ALL_ENDPOINT_REQUESTS = {}
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


def accounting_endpoint_request(request_data):
    """
    Add/create endpoint info in ALL_ENDPOINT_REQUESTS.

    Structure ALL_ENDPOINT_REQUESTS:
    key - endpoint name
    value - EndpointStats object
    """
    if not request_data['url'] in ALL_ENDPOINT_REQUESTS:
        endpoint_stats_class = EndpointStats(request_data['url'])
        ALL_ENDPOINT_REQUESTS[endpoint_stats_class.url] = endpoint_stats_class

    ALL_ENDPOINT_REQUESTS[request_data['url']].add_request()
    ALL_ENDPOINT_REQUESTS[request_data['url']].add_response_time(request_data['response_time'])


def parsing_file(opened_file):
    """Extract data."""
    line = opened_file.readline()
    while line != '':
        request_data = json.loads(line)
        accounting_endpoint_request(request_data)
        line = opened_file.readline()


def read_files(files):
    """Open all files one by one."""
    for file in files:
        with open(file, 'r') as opened_file:
            parsing_file(opened_file)


def main():
    """Execute the script step by step."""
    args = get_command_line_options()
    read_files(args.file)
    pass


if __name__ == '__main__':
    main()
