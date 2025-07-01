# config.py

import streamlit as st

class Settings:
    """
    Application configuration settings loaded from Streamlit's secrets management.
    """
    # Get secrets from st.secrets dictionary
    CLIENT_ID = st.secrets.get("CLIENT_ID")
    CLIENT_SECRET = st.secrets.get("CLIENT_SECRET")
    TENANT_ID = st.secrets.get("TENANT_ID")
    
    # Construct the authority URL from the tenant ID
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    
    # Define the required API scopes
    GRAPH_API_SCOPES = ["https://graph.microsoft.com/.default"]
    
    # Get OneDrive/SharePoint specific settings
    ONEDRIVE_USER_ID = st.secrets.get("ONEDRIVE_USER_ID")
    TARGET_FILE_PATH = st.secrets.get("TARGET_FILE_PATH")
    EXCEL_SHEET_NAME = st.secrets.get("EXCEL_SHEET_NAME")

# Create a single instance of the settings to be used throughout the app
settings = Settings()

# Optional: Add a check to ensure secrets are loaded when running on the cloud
if not all([settings.CLIENT_ID, settings.CLIENT_SECRET, settings.TENANT_ID]):
    # This message will show up in the logs on Streamlit Cloud if secrets are missing
    st.error("Authentication secrets (CLIENT_ID, CLIENT_SECRET, TENANT_ID) are not set. Please add them to your Streamlit Cloud secrets.")

