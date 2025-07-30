"""Module with tests."""

from unittest import mock

import main


class TestMainFunc:
    """Tests main()."""

    @mock.patch('main.get_command_line_options')
    def test_call_get_command_line_options(self, mock_get_command_line_options):
        """Test call mock_get_command_line_options()."""
        main.main()
        mock_get_command_line_options.assert_called_once()
