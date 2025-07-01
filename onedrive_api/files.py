# onedrive_api/files.py
import requests
from io import BytesIO
from .auth import get_access_token
from .errors import OneDriveFileError
from config import settings

def get_onedrive_file_content():
    """
    Downloads a specific Excel file from a user's OneDrive.
    """
    try:
        access_token = get_access_token()
    except Exception as e:
        raise OneDriveFileError(f"Authentication failed: {e}")

    # --- THIS IS THE CORRECT URL FOR A USER'S ONEDRIVE ---
    file_url = (
        f"https://graph.microsoft.com/v1.0/users/{settings.ONEDRIVE_USER_ID}"
        f"/drive/root:{settings.TARGET_FILE_PATH}:/content"
    )

    headers = { 'Authorization': f'Bearer {access_token}' }
    response = requests.get(file_url, headers=headers)

    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise OneDriveFileError(
            f"Failed to download file. Status: {response.status_code}, "
            f"Response: {response.text}"
        )