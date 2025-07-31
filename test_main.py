"""Module with tests."""

import sys
from argparse import Namespace
from unittest import mock

import pytest

import main


class TestGlobalValues:
    """Tests global values."""

    def test_name_average_report_name(self):
        """Test name AVERAGE_REPORT_NAME."""
        assert main.AVERAGE_REPORT_NAME == 'average'


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
