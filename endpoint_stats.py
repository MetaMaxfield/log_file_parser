"""Module with EndpointStats."""

from config import AVERAGE_HEADERS, AVG_RESPONSE_TIME_COLUMN_NAME, REQUESTS_TOTAL_COLUMN_NAME, URL_COLUMN_NAME


class EndpointStats:
    """Collecting statistics for a single endpoint."""

    def __init__(self, url: str):
        """
        Set up initial values.

        self.url - endpoint name
        self.total_response_time - total time of all responses
        self.total_requests - total number of requests
        """
        self.url = url
        self.total_response_time = 0.0
        self.total_requests = 0

    def get_avg_response_time(self) -> float:
        """Calculate average response time."""
        avg_response_time = self.total_response_time / self.total_requests
        return round(avg_response_time, 3)

    def get_correct_format_for_tabulate(self) -> list[str | int | float]:
        """Return the correct format with data for use in forming a table."""
        endpoint_data: list[str | int | float] = []

        for column in AVERAGE_HEADERS:  # Defines a subsequence.
            if column == URL_COLUMN_NAME:
                endpoint_data.append(self.url)
            elif column == REQUESTS_TOTAL_COLUMN_NAME:
                endpoint_data.append(self.total_requests)
            elif column == AVG_RESPONSE_TIME_COLUMN_NAME:
                endpoint_data.append(self.get_avg_response_time())

            else:
                raise Exception('Unknown column in AVERAGE_HEADERS. Add new functionality to EndpointStats.')

        return endpoint_data

    def add_request(self) -> None:
        """Add new request."""
        self.total_requests += 1

    def add_response_time(self, new_response_time: float) -> None:
        """Add new response time in sum times."""
        self.total_response_time += new_response_time
