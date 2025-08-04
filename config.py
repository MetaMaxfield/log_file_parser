"""Script configuration."""

AVERAGE_REPORT_NAME: str = 'average'

URL_COLUMN_NAME: str = 'handler'
REQUESTS_TOTAL_COLUMN_NAME: str = 'total'
AVG_RESPONSE_TIME_COLUMN_NAME: str = 'avg_response_time'

# Also defines a subsequence.
AVERAGE_HEADERS: list[str] = [URL_COLUMN_NAME, REQUESTS_TOTAL_COLUMN_NAME, AVG_RESPONSE_TIME_COLUMN_NAME]
