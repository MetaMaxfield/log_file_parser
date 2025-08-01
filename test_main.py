"""Module with tests."""

import sys
from argparse import Namespace
from unittest import mock

import pytest

import main
from endpoint_stats import EndpointStats


class TestGlobalValues:
    """Tests global values."""

    def test_name_average_report_name(self):
        """Test name AVERAGE_REPORT_NAME."""
        assert main.AVERAGE_REPORT_NAME == 'average'

    def test_value_all_endpoint_requests(self):
        """Test value ALL_ENDPOINT_REQUESTS."""
        assert main.ALL_ENDPOINT_REQUESTS == {}


class TestMainFunc:
    """Tests main()."""

    @mock.patch('main.get_command_line_options')
    def test_call_get_command_line_options(self, mock_get_command_line_options):
        """Test call mock_get_command_line_options()."""
        main.main()
        mock_get_command_line_options.assert_called_once()

    @mock.patch('main.read_files')
    def test_call_read_files(self, mock_read_files):
        """Test call read_files(files)."""
        test_files = ['example3.log', 'example4.log']

        with mock.patch('main.get_command_line_options') as mock_get_command_line_options:
            mock_get_command_line_options.return_value = mock.Mock(file=test_files, report=main.AVERAGE_REPORT_NAME)
            main.main()

        mock_read_files.assert_called_once_with(test_files)


class TestGetCommandLineOptions:
    """Tests get_command_line_options()."""

    @pytest.mark.parametrize(
        'test_command_line_args, expected_files, expected_report',
        [
            (
                ['main.py', '--file', 'file1.log', 'file2.log', '--report', 'average'],
                ['file1.log', 'file2.log'],
                'average',
            ),
            (
                ['main.py', '--file', 'absolute/path/file1.log', 'relative_path/file2.log', '--report', 'average'],
                ['absolute/path/file1.log', 'relative_path/file2.log'],
                'average',
            ),
            (['main.py', '--file', 'example.log'], ['example.log'], 'average'),  # default --report average
        ],
    )
    def test_return_value(self, test_command_line_args, expected_files, expected_report, monkeypatch):
        """Tests return value."""
        monkeypatch.setattr(sys, 'argv', test_command_line_args)  # Replace command line args.

        args = main.get_command_line_options()
        assert isinstance(args, Namespace) is True
        assert args.file == expected_files
        assert args.report == expected_report


class TestReadFiles:
    """Tests read_files(files)."""

    @mock.patch('main.parsing_file')
    def test_call_parsing_file(self, mock_parsing_file):
        """Test call parsing_file(opened_file)."""
        with mock.patch('main.open', new_callable=mock.mock_open) as mock_open:  # Use mock.mock_open!
            main.read_files(
                [
                    'test_file.log',
                ]
            )

        mock_parsing_file.assert_called_once_with(mock_open.return_value)


class TestAccountingEndpointRequest:
    """Tests accounting_endpoint_request(request_data)."""

    def test_working(self):
        """Test working."""
        test_request_data = (
            {
                "@timestamp": "2025-06-22T13:57:32+00:00",
                "status": 200,
                "url": "/api/context/...",
                "request_method": "GET",
                "response_time": 0.024,
                "http_user_agent": "...",
            },
            {
                "@timestamp": "2025-06-22T13:57:32+00:00",
                "status": 200,
                "url": "/api/context/...",
                "request_method": "GET",
                "response_time": 0.02,
                "http_user_agent": "...",
            },
            {
                "@timestamp": "2025-06-22T13:57:32+00:00",
                "status": 200,
                "url": "/api/homeworks/...",
                "request_method": "GET",
                "response_time": 0.024,
                "http_user_agent": "...",
            },
            {
                "@timestamp": "2025-06-22T13:57:34+00:00",
                "status": 200,
                "url": "/api/specializations/...",
                "request_method": "GET",
                "response_time": 0.04,
                "http_user_agent": "...",
            },
        )
        expected_all_endpoint_requests = {  # From test_request_data.
            '/api/context/...': {'total_response_time': 0.044, 'total_requests': 2},
            '/api/homeworks/...': {'total_response_time': 0.024, 'total_requests': 1},
            '/api/specializations/...': {'total_response_time': 0.04, 'total_requests': 1},
        }

        for data in test_request_data:  # Add data from file.
            main.accounting_endpoint_request(data)

        for key, value in main.ALL_ENDPOINT_REQUESTS.items():
            # Check true key (url).
            assert key in expected_all_endpoint_requests
            # Check true value class object.
            assert isinstance(value, EndpointStats) is True
            # Check true EndpointStats(key).total_response_time.
            assert value.total_response_time == expected_all_endpoint_requests[key]['total_response_time']
            # Check true EndpointStats(key).total_requests.
            assert value.total_requests == expected_all_endpoint_requests[key]['total_requests']
