# main.py (Temporary Diagnostic Script)
import requests
import json
from onedrive_api.auth import get_access_token
from dashboard_app import streamlit_app


def find_site_id():
    """
    Connects to the Graph API and searches for a SharePoint site.
    """
    print("Attempting to get access token...")
    try:
        token = get_access_token()
        print("Successfully acquired access token.")
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    # This is the same search we tried in Graph Explorer
    search_url = "https://graph.microsoft.com/v1.0/sites?search=feltol-my.sharepoint.com"

    headers = {'Authorization': f'Bearer {token}'}

    print(f"Searching for site with URL: {search_url}")

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        print("\n--- SUCCESS! Found Site Information: ---")
        # Pretty-print the JSON response
        print(json.dumps(response.json(), indent=4))
        print("\n--- END OF RESPONSE ---")
        print("\nACTION: Look in the 'value' array above for your site and copy the ENTIRE 'id' string.")
    else:
        print(f"\n--- ERROR ---")
        print(f"Failed to find site. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    # This calls the main_dashboard function from your streamlit_app.py file
    streamlit_app.main_dashboard()