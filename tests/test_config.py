"""Tests config.py."""

import config


class TestGlobalValues:
    """Tests config values."""

    def test_name_average_report_name(self):
        """Test name AVERAGE_REPORT_NAME."""
        assert config.AVERAGE_REPORT_NAME == 'average'

    def test_name_url_column_name(self):
        """Test name URL_COLUMN_NAME."""
        assert config.URL_COLUMN_NAME == 'handler'

    def test_name_REQUESTS_total_column_name(self):
        """Test name REQUESTS_TOTAL_COLUMN_NAME."""
        assert config.REQUESTS_TOTAL_COLUMN_NAME == 'total'

    def test_name_AVG_RESPONSE_TIME_column_name(self):
        """Test name AVG_RESPONSE_TIME_COLUMN_NAME."""
        assert config.AVG_RESPONSE_TIME_COLUMN_NAME == 'avg_response_time'

    def test_value_average_headers(self):
        """Test value AVERAGE_HEADERS."""
        assert config.AVERAGE_HEADERS == [
            config.URL_COLUMN_NAME,
            config.REQUESTS_TOTAL_COLUMN_NAME,
            config.AVG_RESPONSE_TIME_COLUMN_NAME,
        ]
