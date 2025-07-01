# Excel OneDrive Dashboard

This project builds a web dashboard using Streamlit that visualizes data from an Excel file stored in a OneDrive for Business account.

## Features

- Securely authenticates with Microsoft Graph API using OAuth 2.0.
- Fetches the latest version of an Excel file directly from OneDrive.
- Processes and cleans the data using pandas.
- Displays interactive charts and tables using Streamlit.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd excel_onedrive_dashboard
    ```

2.  **Create an Azure App Registration:**
    - Go to the Azure portal and register a new application.
    - Create a client secret.
    - Grant it the `Files.Read.All` (or similar) Application permission for Microsoft Graph.
    - Grant admin consent for the permissions in the Azure portal.

3.  **Configure Environment Variables:**
    - Rename `.env.example` to `.env` (or create it).
    - Fill in the values for `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`, `ONEDRIVE_USER_ID`, and `TARGET_FILE_PATH`.

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Launch the Streamlit application by running:

```bash
streamlit run main.py
```