"""Parse a file with logs."""

import argparse
import json

from tabulate import tabulate

from endpoint_stats import EndpointStats

ALL_ENDPOINT_REQUESTS = {}

AVERAGE_REPORT_NAME = 'average'
AVERAGE_HEADERS = ['handler', 'total', 'avg_response_time']  # Also defines a subsequence.


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


def generate_average_format_for_table():
    """
    Generate data format: [(...), (...)].

    Determine subsequence in AVERAGE_HEADERS.
    Order by '-total'.
    """
    table_data = [value.get_correct_format_for_tabulate() for value in ALL_ENDPOINT_REQUESTS.values()]
    table_data.sort(key=lambda x: 1 / x[AVERAGE_HEADERS.index('total')])
    return table_data


def create_table(type_report):
    """Create table object according to the given '--report'."""
    if type_report == AVERAGE_REPORT_NAME:
        table_data = generate_average_format_for_table()
        table = tabulate(table_data, headers=AVERAGE_HEADERS, showindex='always')
    else:
        raise Exception(f'No action specified for parameter "--report {type_report}" in "create_table(type_report)".')
    return table


def main():
    """Execute the script step by step."""
    args = get_command_line_options()
    read_files(args.file)
    _ = create_table(args.report)
    pass


if __name__ == '__main__':
    main()
