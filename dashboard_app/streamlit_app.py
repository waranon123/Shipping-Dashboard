# dashboard_app/streamlit_app.py

import streamlit as st
import pandas as pd
import datetime
import time
import numpy as np # Import numpy to handle NaN values
import streamlit.components.v1 as components # Import for rendering raw HTML

# These imports are still needed to load the data
from data_processing import loader, cleaning
from onedrive_api.errors import OneDriveError

def get_status_style(status_text):
    """
    Returns a background and text color based on the status text from Excel.
    """
    status = str(status_text).strip()
    if 'Finished' in status:
        return 'background-color: #28a745; color: white; font-weight: bold;'
    elif 'Delay' in status:
        return 'background-color: #dc3545; color: white; font-weight: bold;'
    elif 'On Process' in status:
        return 'background-color: #ffc107; color: black; font-weight: bold;'
    return 'background-color: white; color: black; font-weight: bold;' # Default style

def format_time_display(value):
    """
    Helper function to format time values from Excel into HH:MM strings.
    Returns '-' if the value is not a valid time. This version is more robust.
    """
    if pd.isna(value):
        return '-'
    try:
        # This will attempt to convert strings like '16:25' or '09:20:00 AM'
        # and also handle existing datetime/time objects.
        # The format string %H:%M ensures we only get hours and minutes.
        return pd.to_datetime(str(value), errors='raise').strftime('%H:%M')
    except (ValueError, TypeError):
        # If any conversion fails, return a dash
        return '-'

def format_value_display(value):
    """
    Helper function to format values for display.
    - Shows integers for numbers like Ter. and Ship no.
    - Shows a dash for blank cells.
    - Shows other values as they are.
    """
    if pd.isna(value):
        return '-'
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def format_status_display(status_value):
    """
    Helper function to format the status text with icons.
    Returns '-' if the status is blank or NaN.
    """
    if pd.isna(status_value) or status_value == '':
        return '-'
    
    status = str(status_value).strip()
    if status == 'On Process':
        return f"⏳ {status}"
    elif status == 'Delay(F)':
        return f"❗ {status}"
    elif status == 'Finished':
        return f"✅ {status}"
    return status # Return the value as-is if it's something unexpected


def main_dashboard():
    """
    The main function to build the new advanced Shipping Board Status dashboard.
    """
    st.set_page_config(layout="wide")

    # --- CUSTOM CSS INJECTION ---
    st.markdown("""
    <style>
        /* Style for main headers - smaller and left-aligned */
        .big-header {
            font-size: 2.5rem !important;
            font-weight: bold !important;
            color: #1E3A8A !important;
            padding: 0.5rem 0 !important;
            margin-bottom: 1rem !important;
            text-align: left !important;
            background-color: transparent !important;
            border-bottom: 3px solid #DBEAFE;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- INITIALIZE SESSION STATE ---
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'last_load_time' not in st.session_state:
        st.session_state.last_load_time = None
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    if 'next_update' not in st.session_state:
        st.session_state.next_update = datetime.datetime.now()
    if 'next_carousel_slide' not in st.session_state:
        st.session_state.next_carousel_slide = datetime.datetime.now()


    # --- DATA LOADING FUNCTION ---
    def load_data_from_onedrive(force_rerun=False):
        with st.spinner("Connecting to OneDrive and fetching data..."):
            try:
                raw_df = loader.load_excel_from_onedrive()
                cleaned_df = cleaning.clean_data(raw_df)
                
                if 'Completion time' in cleaned_df.columns:
                    cleaned_df['Completion time'] = pd.to_datetime(cleaned_df['Completion time'], errors='coerce')

                st.session_state.data = cleaned_df
                st.session_state.error = None
                st.session_state.last_load_time = datetime.datetime.now()
            except Exception as e:
                st.session_state.error = f"An error occurred: {e}"
                st.session_state.data = None
        
        if force_rerun:
            st.rerun()

    # --- SIDEBAR FOR CONTROLS ---
    with st.sidebar:
        st.header("🚚 Actions & Settings")
        if st.button("🔄 Load/Refresh Data"):
            load_data_from_onedrive(force_rerun=True)

        if st.session_state.last_load_time:
            st.caption(f"Data last loaded: {st.session_state.last_load_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.header("Self-Update")
        # The toggle has been removed. Self-update is now always on.
        refresh_interval = st.number_input("Refresh interval (s)", min_value=10, max_value=3600, value=60)
        
        st.divider()

        # --- NEW COLLAPSIBLE FILTER SECTION ---
        with st.expander("📊 Data Filters", expanded=True):
            # --- SMART DATE FILTER ---
            if st.session_state.data is not None and not st.session_state.data.empty and 'Completion time' in st.session_state.data:
                min_date = st.session_state.data['Completion time'].dropna().min().date()
                max_date = st.session_state.data['Completion time'].dropna().max().date()
            else:
                min_date = datetime.date.today() - datetime.timedelta(days=30)
                max_date = datetime.date.today()

            start_date = st.date_input("Start Date", value=min_date, format="YYYY-MM-DD")
            end_date = st.date_input("End Date", value=max_date, format="YYYY-MM-DD")
            
            if start_date > end_date:
                st.error("Error: End date must be after start date.")
            
            # --- FILTERS WITH SELECTBOX (DROPDOWN) ---
            if st.session_state.data is not None:
                all_terminals = ['All'] + sorted(st.session_state.data['Ter.'].dropna().unique())
                selected_terminal = st.selectbox("Filter by Terminal", options=all_terminals)

                all_ship_nos = ['All'] + sorted(st.session_state.data['Ship no.'].dropna().unique())
                selected_ship_no = st.selectbox("Filter by Ship no.", options=all_ship_nos)
        
        st.divider()

        st.header("🖥️ Display Mode")
        carousel_enabled = st.toggle("Enable Carousel View", value=False)
        if carousel_enabled:
            carousel_interval = st.number_input("Carousel interval (seconds)", min_value=5, max_value=60, value=10)
            rows_per_page = st.number_input("Rows per page", min_value=1, max_value=50, value=7)

    # --- Initial Data Load ---
    if st.session_state.data is None:
        load_data_from_onedrive()

    # --- STABLE SELF-UPDATE LOGIC ---
    now = datetime.datetime.now()
    if now >= st.session_state.next_update:
        load_data_from_onedrive()
        st.session_state.next_update = now + datetime.timedelta(seconds=refresh_interval)
        st.rerun()

    # --- MAIN DASHBOARD DISPLAY ---
    if st.session_state.data is not None:
        df = st.session_state.data.copy()

        # --- DATA VALIDATION ---
        required_cols = ['Completion time', 'Ter.', 'Dock Code', 'Truck Route', 'Status Preparation', 'Status Loading', 'Ship no.', 'Preparation Start', 'Preparation End', 'Loading Start', 'Loading End']
        if not all(col in df.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in df.columns]
            st.error(f"Error: The following required columns are missing from the Excel file: {', '.join(missing_cols)}")
            st.warning("Please check the 'Databaseshippingboard' sheet in your Excel file.")
            st.subheader("Columns Found:")
            st.write(list(df.columns))
        else:
            # Filter by date range using 'Completion time'
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
            date_mask = (df['Completion time'] >= start_datetime) & (df['Completion time'] <= end_datetime)
            filtered_df = df.loc[date_mask].copy()

            # Apply single-select filters
            if 'selected_terminal' in locals() and selected_terminal != 'All':
                filtered_df = filtered_df[filtered_df['Ter.'] == selected_terminal]
            if 'selected_ship_no' in locals() and selected_ship_no != 'All':
                filtered_df = filtered_df[filtered_df['Ship no.'] == selected_ship_no]
            
            if filtered_df.empty:
                st.info("No shipping data found for the selected filters.")
                
            else:
                # --- CAROUSEL LOGIC WITH PAGINATION ---
                carousel_items = []
                if carousel_enabled:
                    # First, add paginated views for each terminal
                    unique_terminals = sorted(filtered_df['Ter.'].dropna().unique())
                    for terminal in unique_terminals:
                        terminal_df = filtered_df[filtered_df['Ter.'] == terminal]
                        num_shipments = len(terminal_df)
                        num_pages = int(np.ceil(num_shipments / rows_per_page))
                        for page in range(num_pages):
                            carousel_items.append({'type': 'terminal', 'value': terminal, 'page': page})
                    
                    # Then, add views for each individual shipment number
                    unique_shipments = sorted(filtered_df['Ship no.'].dropna().unique())
                    for ship_no in unique_shipments:
                        carousel_items.append({'type': 'shipment', 'value': ship_no, 'page': 0})


                display_df = filtered_df
                metrics_df = filtered_df
                metrics_header_text = "Key Metrics for Filtered Data"
                
                if carousel_enabled and carousel_items:
                    if st.session_state.carousel_index >= len(carousel_items):
                        st.session_state.carousel_index = 0
                    
                    current_item = carousel_items[st.session_state.carousel_index]
                    item_type = current_item['type']
                    item_value = current_item['value']
                    
                    if item_type == 'terminal':
                        current_page = current_item['page']
                        terminal_df = filtered_df[filtered_df['Ter.'] == item_value]
                        start_row = current_page * rows_per_page
                        end_row = start_row + rows_per_page
                        display_df = terminal_df.iloc[start_row:end_row]
                        metrics_df = terminal_df
                        
                        display_val = int(item_value)
                        total_pages = int(np.ceil(len(terminal_df) / rows_per_page))
                        page_indicator = f" (Page {current_page + 1}/{total_pages})" if total_pages > 1 else ""
                        st.markdown(f"<p class='big-header'>Shipment Details for: Ter. {display_val}{page_indicator}</p>", unsafe_allow_html=True)
                        metrics_header_text = f"Key Metrics for: Ter. {display_val}"
                    
                    elif item_type == 'shipment':
                        display_df = filtered_df[filtered_df['Ship no.'] == item_value]
                        metrics_df = display_df
                        st.markdown(f"<p class='big-header'>Shipment Details for: Ship no. {item_value}</p>", unsafe_allow_html=True)
                        metrics_header_text = f"Key Metrics for: Ship no. {item_value}"

                else:
                    st.markdown("<p class='big-header'>Shipment Details</p>", unsafe_allow_html=True)

                # --- BUILD CUSTOM HTML TABLE ---
                html_table = """
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                    <thead style="background-color: #F0F4FF; color: #1E3A8A;">
                        <tr>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Ter.</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Ship no.</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Dock Code</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Truck Route</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 0.2rem; text-align: center; border: 1px solid #ddd;">Preparation Start</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 0.2rem; text-align: center; border: 1px solid #ddd;">Preparation End</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Loading Start</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Loading End</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">Status Preparation</th>
                            <th style="font-size: 1.8rem; font-weight: bold; padding: 2rem; text-align: center; border: 1px solid #ddd;">Status Loading</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for _, row in display_df.iterrows():
                    ter_display = format_value_display(row['Ter.'])
                    ship_no_display = format_value_display(row['Ship no.'])
                    prep_start_display = format_time_display(row['Preparation Start'])
                    prep_end_display = format_time_display(row['Preparation End'])
                    load_start_display = format_time_display(row['Loading Start'])
                    load_end_display = format_time_display(row['Loading End'])
                    
                    prep_status_text = format_status_display(row['Status Preparation'])
                    load_status_text = format_status_display(row['Status Loading'])
                    
                    prep_style = get_status_style(row['Status Preparation'])
                    load_style = get_status_style(row['Status Loading'])
                    
                    html_table += f"""
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{ter_display}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{ship_no_display}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{format_value_display(row['Dock Code'])}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{format_value_display(row['Truck Route'])}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{prep_start_display}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{prep_end_display}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{load_start_display}</td>
                        <td style="font-size: 1.5rem; font-weight: bold; padding: 1rem; text-align: center; border: 1px solid #ddd;">{load_end_display}</td>
                        <td style="{prep_style}; font-size: 1.5rem; padding: 1rem; text-align: center; border: 2px solid #ddd;">{prep_status_text}</td>
                        <td style="{load_style}; font-size: 1.5rem; padding: 1rem; text-align: center; border: 1px solid #ddd;">{load_status_text}</td>
                    </tr>
                    """
                html_table += "</tbody></table>"
                
                table_height = (len(display_df) * 120) + 80
                components.html(html_table, height=table_height, scrolling=True)

                # --- KEY METRICS ---
                st.markdown(f"<p class='big-header'>{metrics_header_text}</p>", unsafe_allow_html=True)
                total_shipments = len(metrics_df)
                prep_counts = metrics_df['Status Preparation'].value_counts()
                load_counts = metrics_df['Status Loading'].value_counts()
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Shipments", total_shipments)
                col2.metric("Prep On Process", prep_counts.get('On Process', 0))
                col3.metric("Prep Delayed", prep_counts.get('Delay', 0))
                col4.metric("Prep Finished", prep_counts.get('Finished', 0))
                col5, col6, col7, _ = st.columns(4)
                col5.metric("Load On Process", load_counts.get('On Process', 0))
                col6.metric("Load Delayed", load_counts.get('Delay', 0))
                col7.metric("Load Finished", load_counts.get('Finished', 0))

    elif st.session_state.error:
        st.error(f"Could not display dashboard due to a previous error: {st.session_state.error}")
    else:
        st.info("Click the 'Load/Refresh Data' button in the sidebar to start.")

    # --- STABLE TIMING LOGIC ---
    if carousel_enabled and 'carousel_items' in locals() and carousel_items:
        if now >= st.session_state.next_carousel_slide:
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_items)
            st.session_state.next_carousel_slide = now + datetime.timedelta(seconds=carousel_interval)
            st.rerun()
    
    # This keeps the app alive for the timers to work
    time.sleep(1)
    st.rerun()
