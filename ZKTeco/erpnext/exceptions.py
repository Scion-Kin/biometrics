class AttendanceFetchError(Exception):
    """Exception raised for errors in fetching attendance data."""
    def __init__(self, message="Failed to fetch attendance data. Please check the user ID or network connection."):
        self.message = message
        super().__init__(self.message)

class InvalidResponseError(Exception):
    """Exception raised for invalid responses from the API."""
    def __init__(self, message="Received an invalid response from the API. Please check the API endpoint or your request parameters."):
        self.message = message
        super().__init__(self.message)

class NetworkError(Exception):
    """Exception raised for network-related errors."""
    def __init__(self, message="Network error occurred. Please check your internet connection or the API server status."):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    def __init__(self, message="Configuration error. Please check your MilMall API settings or environment variables."):
        self.message = message
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Exception raised for authentication-related errors."""
    def __init__(self, message="Authentication error. Please check your API credentials or token."):
        self.message = message
        super().__init__(self.message)

class UnknownResponseError(Exception):
    """Exception raised for unknown response errors."""
    def __init__(self, message="Received an unknown response from the API. Please check the API documentation or your request parameters."):
        self.message = message
        super().__init__(self.message)
