# onedrive_api/errors.py

class OneDriveError(Exception):
    """Base exception for OneDrive API errors."""
    pass

class OneDriveAuthError(OneDriveError):
    """Raised for authentication-related errors."""
    pass

class OneDriveFileError(OneDriveError):
    """Raised for file operation errors."""
    pass