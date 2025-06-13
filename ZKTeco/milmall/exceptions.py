class LoginError(Exception):
    """Exception raised for errors in the login process."""
    def __init__(self, message="Login failed due to invalid credentials or connection issues."):
        self.message = message
        super().__init__(self.message)

class TokenRefreshError(Exception):
    """Exception raised for errors in refreshing the access token."""
    def __init__(self, message="Failed to refresh the access token. Please check your credentials or network connection."):
        self.message = message
        super().__init__(self.message)

class AttendanceFetchError(Exception):
    """Exception raised for errors in fetching attendance data."""
    def __init__(self, message="Failed to fetch attendance data. Please check the user ID or network connection."):
        self.message = message
        super().__init__(self.message)

class UserNotFoundError(Exception):
    """Exception raised when a user is not found in the system."""
    def __init__(self, message="User not found. Please check the user ID or ensure the user exists."):
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
