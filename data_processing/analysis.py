# data_processing/analysis.py
import pandas as pd

def get_shipments_by_route(df: pd.DataFrame) -> pd.DataFrame:
    """
    Counts the number of shipments for each unique truck route.
    """
    # Check if the required columns exist in the DataFrame
    if 'Truck Route' in df.columns and 'Ship no.' in df.columns:
        # Group by the 'Truck Route' and count the number of shipments
        analysis_df = df.groupby('Truck Route')['Ship no.'].count().reset_index()

        # Rename the columns for a clearer chart label
        analysis_df = analysis_df.rename(columns={'Ship no.': 'Number of Shipments'})

        # Sort the results for a nicer chart
        return analysis_df.sort_values(by='Number of Shipments', ascending=False)

    # If the columns don't exist, return an empty DataFrame
    return pd.DataFrame()