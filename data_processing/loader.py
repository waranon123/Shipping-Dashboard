# data_processing/loader.py
import pandas as pd
from onedrive_api import files
from config import settings # <-- Add this import

def load_excel_from_onedrive(sheet_name=0):
    """
    Loads data from the specified Excel file on OneDrive into a pandas DataFrame.

    Args:
        sheet_name (str or int, optional): The name or index of the sheet to read. Defaults to 0.

    Returns:
        pd.DataFrame: A DataFrame containing the Excel data.
    """ 
    try:
        file_content_stream = files.get_onedrive_file_content()
        # Use the sheet name from the config settings
        df = pd.read_excel(file_content_stream, sheet_name=settings.EXCEL_SHEET_NAME, engine='openpyxl')
        return df
    except Exception as e:
        # Propagate the error or handle it as needed
        raise e
