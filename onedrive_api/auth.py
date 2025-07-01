# onedrive_api/auth.py
import msal
from .errors import OneDriveAuthError
from config import settings

def get_access_token():
    """
    Acquires an access token from Azure AD using the client credentials flow.

    Returns:
        str: The access token.
    
    Raises:
        OneDriveAuthError: If token acquisition fails.
    """
    app = msal.ConfidentialClientApplication(
        client_id=settings.CLIENT_ID,
        authority=settings.AUTHORITY,
        client_credential=settings.CLIENT_SECRET,
    )

    # First, try to get a token from the cache
    result = app.acquire_token_silent(scopes=settings.GRAPH_API_SCOPES, account=None)

    # If no suitable token is in the cache, acquire a new one from Azure AD
    if not result:
        result = app.acquire_token_for_client(scopes=settings.GRAPH_API_SCOPES)

    if "access_token" in result:
        return result['access_token']
    else:
        error_description = result.get("error_description", "No error description provided.")
        raise OneDriveAuthError(f"Could not acquire access token: {error_description}")