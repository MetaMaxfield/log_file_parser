"""Module with tests."""

import json
import os
import re
import runpy
import sys
from argparse import Namespace
from pathlib import Path
from unittest import mock

import main
import pytest
from config import AVERAGE_HEADERS, AVERAGE_REPORT_NAME, REQUESTS_TOTAL_COLUMN_NAME
from endpoint_stats import EndpointStats
from tabulate import tabulate


@pytest.fixture(autouse=True)
def autoclear_all_endpoint_requests():
    """Autoclear ALL_ENDPOINT_REQUESTS between tests."""
    main.ALL_ENDPOINT_REQUESTS.clear()


def test_value_all_endpoint_requests():
    """Test value ALL_ENDPOINT_REQUESTS."""
    assert main.ALL_ENDPOINT_REQUESTS == {}


class TestMainFunc:
    """Tests main()."""

    @mock.patch('main.get_command_line_options')
    def test_call_get_command_line_options(self, mock_get_command_line_options):
        """Test call mock_get_command_line_options()."""
        mock_get_command_line_options.side_effect = SystemExit
        with pytest.raises(SystemExit):
            main.main()
        mock_get_command_line_options.assert_called_once()

    @mock.patch('main.read_files')
    def test_call_read_files(self, mock_read_files):
        """Test call read_files(files)."""
        test_files = ['example3.log', 'example4.log']

        with mock.patch('main.get_command_line_options') as mock_get_command_line_options:
            mock_get_command_line_options.return_value = mock.Mock(file=test_files, report=AVERAGE_REPORT_NAME)
            main.main()

        mock_read_files.assert_called_once_with(test_files)

    @mock.patch('main.read_files', return_value=None)
    @mock.patch('main.get_command_line_options', return_value=mock.Mock(file=['testfile1.log'], report='test_report'))
    def test_call_create_table(self, *args):
        """Test call create_table(type_report)."""
        with mock.patch('main.create_table') as mock_create_table:
            main.main()
            mock_create_table.assert_called_once_with('test_report')

    @mock.patch('main.create_table', return_value='String with table')
    @mock.patch('main.read_files', return_value=None)
    @mock.patch('main.get_command_line_options', return_value=mock.Mock(file=['testfile1.log'], report='test_report'))
    def test_call_print(self, *args):
        """Test call print() with table='String with table'."""
        with mock.patch('main.print') as mock_print:
            main.main()
            mock_print.assert_called_once_with('String with table')


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


class TestCreateTable:
    """Tests create_table(type_report)."""

    @mock.patch('main.generate_average_format_for_table', side_effect=SystemExit)
    def test_call_generate_average_format_for_table(self, mock_generate_average_format_for_table):
        """Test call generate_average_format_for_table() for type_report=AVERAGE_REPORT_NAME."""
        with pytest.raises(SystemExit):  # Stop run after call create_table(type_report).
            _ = main.create_table(AVERAGE_REPORT_NAME)
        mock_generate_average_format_for_table.assert_called_once()

    def test_raise(self):
        """Test call exception due to unknown type report."""
        unknown_type_report = 'UNKNOWN_TYPE_REPORT'
        with pytest.raises(
            Exception,
            match=re.escape(  # match uses regex (use re.escape).
                f'No action specified for parameter "--report {unknown_type_report}" in "create_table(type_report)".'
            ),
        ):
            _ = main.create_table(unknown_type_report)

    @mock.patch('main.generate_average_format_for_table')
    def test_return_value_for_average_type(self, mock_generate_average_format_for_table):
        """Test return value for type_report=AVERAGE_REPORT_NAME."""
        # Create ident return value from generate_average_format_for_table()
        # Count values == len(AVERAGE_HEADERS)
        test_return_value = []
        test_return_value.append([f'random_value{i}' for i in range(len(AVERAGE_HEADERS))])

        mock_generate_average_format_for_table.return_value = test_return_value

        fact_table = main.create_table(AVERAGE_REPORT_NAME)
        expected_table = tabulate(test_return_value, headers=AVERAGE_HEADERS, showindex='always')

        assert fact_table == expected_table


class TestGenerateAverageFormatForTable:
    """Tests generate_average_format_for_table()."""

    def test_return_value(self):
        """Test return value."""
        # Create objects for ALL_ENDPOINT_REQUESTS.
        # Create endpoint_stats1
        endpoint_stats1 = EndpointStats('/path/1/...')
        endpoint_stats1.total_response_time = 1.5
        endpoint_stats1.total_requests = 3
        # Create endpoint_stats2
        endpoint_stats2 = EndpointStats('/path/2/...')
        endpoint_stats2.total_response_time = 2
        endpoint_stats2.total_requests = 2
        # Create endpoint_stats3
        endpoint_stats3 = EndpointStats('/path/3/...')
        endpoint_stats3.total_response_time = 0.3
        endpoint_stats3.total_requests = 1

        # Create ALL_ENDPOINT_REQUESTS.
        main.ALL_ENDPOINT_REQUESTS[endpoint_stats1.url] = endpoint_stats1
        main.ALL_ENDPOINT_REQUESTS[endpoint_stats2.url] = endpoint_stats2
        main.ALL_ENDPOINT_REQUESTS[endpoint_stats3.url] = endpoint_stats3

        # Run generate_average_format_for_table()
        fact_table_data = main.generate_average_format_for_table()

        # Check "fact_table_data == expected_table_data"
        expected_table_data = sorted(
            [
                endpoint_stats1.get_correct_format_for_tabulate(),
                endpoint_stats2.get_correct_format_for_tabulate(),
                endpoint_stats3.get_correct_format_for_tabulate(),
            ],
            key=lambda x: 1 / x[AVERAGE_HEADERS.index(REQUESTS_TOTAL_COLUMN_NAME)],
        )
        assert fact_table_data == expected_table_data


class TestRunFile:
    """Tests run main.py."""

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

    @pytest.fixture(autouse=False)
    def new_local_file1(self):
        """Create new file 'testfile1.log' in local directory and delete this file after test."""
        current_dir = Path(__file__).parent.parent
        log_file_name = 'testfile1.log'
        new_file = current_dir / log_file_name
        with open(new_file, 'w') as file:  # Write in file data from TestRunFile.test_request_data.
            for data in TestRunFile.test_request_data:
                json.dump(data, file)
                file.write('\n')

        yield log_file_name

        os.remove(new_file)

    @pytest.fixture(autouse=False)
    def new_local_file2(self):
        """Create new file 'testfile2.log' in local directory and delete this file after test."""
        current_dir = Path(__file__).parent.parent
        log_file_name = 'testfile2.log'
        new_file = current_dir / log_file_name
        with open(new_file, 'w') as file:  # Write in file data from TestRunFile.test_request_data.
            for data in TestRunFile.test_request_data:
                json.dump(data, file)
                file.write('\n')

        yield log_file_name

        os.remove(new_file)

    @pytest.fixture(autouse=False)
    def new_home_file1(self):
        """Create new file 'testfile1.log' in home directory and delete this file after test."""
        home_dir = Path().home()
        log_file_name = 'testfile1.log'
        new_file = home_dir / log_file_name
        with open(new_file, 'w') as file:  # Write in file data from TestRunFile.test_request_data.
            for data in TestRunFile.test_request_data:
                json.dump(data, file)
                file.write('\n')

        yield str(new_file)

        os.remove(new_file)

    @pytest.fixture(autouse=False)
    def expected_table_file1(self):
        """Expect table for one file (data from TestRunFile.test_request_data)."""
        # Create endpoint_stats1
        endpoint_stats1 = EndpointStats('/api/context/...')
        endpoint_stats1.total_response_time = 0.044
        endpoint_stats1.total_requests = 2
        # Create endpoint_stats2
        endpoint_stats2 = EndpointStats('/api/homeworks/...')
        endpoint_stats2.total_response_time = 0.024
        endpoint_stats2.total_requests = 1
        # Create endpoint_stats3
        endpoint_stats3 = EndpointStats('/api/specializations/...')
        endpoint_stats3.total_response_time = 0.04
        endpoint_stats3.total_requests = 1

        expected_tabulate_data = [
            endpoint_stats1.get_correct_format_for_tabulate(),
            endpoint_stats2.get_correct_format_for_tabulate(),
            endpoint_stats3.get_correct_format_for_tabulate(),
        ]
        expected_table = tabulate(expected_tabulate_data, headers=AVERAGE_HEADERS, showindex='always')
        return expected_table

    @pytest.fixture(autouse=False)
    def expected_table_file1_file2(self):
        """
        Expect table for two files (data from TestRunFile.test_request_data).

        Data values is double because files have a equal data.
        """
        # Create endpoint_stats1
        endpoint_stats1 = EndpointStats('/api/context/...')
        endpoint_stats1.total_response_time = 0.088
        endpoint_stats1.total_requests = 4
        # Create endpoint_stats2
        endpoint_stats2 = EndpointStats('/api/homeworks/...')
        endpoint_stats2.total_response_time = 0.048
        endpoint_stats2.total_requests = 2
        # Create endpoint_stats3
        endpoint_stats3 = EndpointStats('/api/specializations/...')
        endpoint_stats3.total_response_time = 0.08
        endpoint_stats3.total_requests = 2

        expected_tabulate_data = [
            endpoint_stats1.get_correct_format_for_tabulate(),
            endpoint_stats2.get_correct_format_for_tabulate(),
            endpoint_stats3.get_correct_format_for_tabulate(),
        ]
        expected_table = tabulate(expected_tabulate_data, headers=AVERAGE_HEADERS, showindex='always')
        return expected_table

    def test_run_parser_1(self, new_local_file1, expected_table_file1, monkeypatch):
        """
        Run 'python main.py --file testfile1.log'.

        File in local directory, default report (average).
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1)

    def test_run_parser_2(self, new_local_file1, expected_table_file1, monkeypatch):
        """
        Run 'python main.py --file testfile1.log --report average'.

        File in local directory, report is 'average'.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1)

    def test_run_parser_3(self, new_local_file1, new_local_file2, expected_table_file1_file2, monkeypatch):
        """
        Run 'python main.py --file testfile1.log testfile2.log'.

        Two files in local directory, default report.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1, new_local_file2])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1_file2)

    def test_run_parser_4(self, new_local_file1, new_local_file2, expected_table_file1_file2, monkeypatch):
        """
        Run 'python main.py --file testfile1.log testfile2.log --report average'.

        Two files in local directory, report is 'average'.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1, new_local_file2])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1_file2)

    def test_run_parser_5(self, new_home_file1, expected_table_file1, monkeypatch):
        """
        Run 'python main.py --file home/path/testfile1.log --report average'.

        File in home directory, report is 'average'.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_home_file1])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1)

    def test_run_parser_6(self, new_home_file1, new_local_file2, expected_table_file1_file2, monkeypatch):
        """
        Run 'python main.py --file home/path/testfile1.log testfile2.log'.

        One file in home directory, second file in local directory, default report.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_home_file1, new_local_file2])
        with mock.patch('builtins.print') as mock_print:
            runpy.run_path("main.py", run_name="__main__")

        mock_print.assert_called_once_with(expected_table_file1_file2)

    def test_run_parser_7(self, monkeypatch):
        """
        Run 'python main.py --file not_exist_file.log testfile2.log'.

        Not exist file, default report.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', 'not_exist_file.log'])
        with pytest.raises(FileNotFoundError):
            runpy.run_path("main.py", run_name="__main__")

    def test_run_parser_8(self, new_local_file1, monkeypatch):
        """
        Run 'python main.py --file testfile1.log not_exist_file.log testfile2.log'.

        First file in local directory, second file is not exist, default report.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1, 'not_exist_file.log'])
        with pytest.raises(FileNotFoundError):
            runpy.run_path("main.py", run_name="__main__")

    def test_run_parser_9(self, monkeypatch):
        """
        Run 'python main.py --file testfile1.txt'.

        First file in local directory with not json format data, default report.
        """
        current_dir = Path(__file__).parent.parent
        log_file_name = 'test_file.txt'
        new_file = current_dir / log_file_name
        with open(new_file, 'w') as file:  # Create file with not correct format data.
            file.write('Uncorect data format.')

        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', log_file_name])
        with pytest.raises(json.decoder.JSONDecodeError):
            runpy.run_path("main.py", run_name="__main__")

        os.remove(new_file)

    def test_run_parser_10(self, new_local_file1, monkeypatch):
        """
        Run 'python main.py --file testfile1.txt --report unknown_report'.

        First file in local directory, unknown report.
        """
        monkeypatch.setattr(sys, 'argv', ['main.py', '--file', new_local_file1, '--report', 'unknown_report'])
        with pytest.raises(SystemExit) as system_exit:
            runpy.run_path("main.py", run_name="__main__")

        assert system_exit.value.code == 2
