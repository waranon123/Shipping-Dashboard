# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



class Settings:
    """
    Application configuration settings loaded from environment variables.
    """
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    GRAPH_API_SCOPES = ["https://graph.microsoft.com/.default"]
    EXCEL_SHEET_NAME = os.getenv("EXCEL_SHEET_NAME")
    # OneDrive specific settings
    ONEDRIVE_USER_ID = os.getenv("ONEDRIVE_USER_ID")
    TARGET_FILE_PATH = os.getenv("TARGET_FILE_PATH")
    ONEDRIVE_USER_ID = os.getenv("ONEDRIVE_USER_ID")
# Create a single instance of the settings
settings = Settings()

# Validate that all required settings are present
# NEW, CORRECTED CODE
# Validate that all required settings from the .env file are present
required_settings = [
    settings.CLIENT_ID,
    settings.CLIENT_SECRET,
    settings.TENANT_ID,
    settings.TARGET_FILE_PATH,
    settings.EXCEL_SHEET_NAME 
]

if not all(required_settings):
    raise ValueError("One or more required environment variables are missing. Please check your .env file.")