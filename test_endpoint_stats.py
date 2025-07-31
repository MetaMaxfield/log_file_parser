"""Module with tests test_endpoint_stats.py."""

import pytest

from endpoint_stats import EndpointStats


class TestEndpointStats:
    """Tests EndpointStats."""

    endpoint_url = 'test/url/'
    fake_times = [0.024, 0.02, 0.024, 0.06, 0.032]

    @pytest.fixture
    def endpoint_stats_object(self):
        """Create EndpointStats object."""
        return EndpointStats(TestEndpointStats.endpoint_url)

    def test_init_attributes(self, endpoint_stats_object):
        """Test initialization attributes."""
        assert endpoint_stats_object.url == TestEndpointStats.endpoint_url
        assert endpoint_stats_object.total_response_time == 0.0
        assert endpoint_stats_object.total_requests == 0

    def test_get_avg_response_time_return_value(self, endpoint_stats_object):
        """Test get_avg_response_time() return value."""
        for fake_time in TestEndpointStats.fake_times:
            endpoint_stats_object.add_response_time(fake_time)
            endpoint_stats_object.add_request()

        assert endpoint_stats_object.get_avg_response_time() == (
            sum(TestEndpointStats.fake_times) / len(TestEndpointStats.fake_times)
        )

    def test_get_correct_format_for_tabulate_return_value(self, endpoint_stats_object):
        """Test get_correct_format_for_tabulate() return value."""
        for fake_time in TestEndpointStats.fake_times:
            endpoint_stats_object.add_response_time(fake_time)
            endpoint_stats_object.add_request()

        assert endpoint_stats_object.get_correct_format_for_tabulate() == (
            endpoint_stats_object.url,
            endpoint_stats_object.total_requests,
            endpoint_stats_object.get_avg_response_time(),
        )

    def test_add_request(self, endpoint_stats_object):
        """Test add_request() working."""
        for i, _ in enumerate(TestEndpointStats.fake_times):
            endpoint_stats_object.add_request()
            assert endpoint_stats_object.total_requests == i + 1

    def test_add_response_time(self, endpoint_stats_object):
        """Test add_response_time(new_response_time) working."""
        for i, fake_time in enumerate(TestEndpointStats.fake_times):
            endpoint_stats_object.add_response_time(fake_time)
            assert endpoint_stats_object.total_response_time == sum(TestEndpointStats.fake_times[: i + 1])
