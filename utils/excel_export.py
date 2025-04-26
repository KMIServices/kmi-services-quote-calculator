"""
Excel Export Utility

This module provides reliable Excel export functionality for Streamlit applications.
It works across different environments including embedded displays.
"""

import os
import io
import base64
import uuid
import streamlit as st
import pandas as pd
from datetime import datetime

def create_excel_download_button(df, sheet_name="Data", filename=None, 
                               button_text="Download Excel File", 
                               help_text=None, 
                               include_index=False,
                               use_container_width=False):
    """
    Create a download button for Excel export that works in all environments.
    
    Parameters:
    df: DataFrame to export
    sheet_name: Name of the sheet in the Excel file
    filename: Name of the file to download (without extension)
    button_text: Text to display on the button
    help_text: Help text for the button tooltip
    include_index: Whether to include the DataFrame index
    use_container_width: Whether the button should use the full container width
    
    Returns:
    None (displays button on Streamlit app)
    """
    # Create a default filename if none provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"data_export_{timestamp}_{unique_id}"
    
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=include_index)
        
        # Add some formatting
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Add header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#22C7D6',
            'color': 'white',
            'border': 1
        })
        
        # Apply formatting to header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + (1 if include_index else 0), value, header_format)
            
        # Auto-adjust columns
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(str(col)) + 2)
            worksheet.set_column(i + (1 if include_index else 0), i + (1 if include_index else 0), column_len)
    
    # Reset cursor & get value
    output.seek(0)
    excel_data = output.getvalue()
    
    # Create download button using direct base64 encoding (most reliable approach)
    b64 = base64.b64encode(excel_data).decode()
    button_uuid = str(uuid.uuid4())[:8]
    button_id = f'download-excel-{button_uuid}'
    
    # JavaScript function for downloading
    custom_css = f"""
    <style>
    #{button_id} {{
        background-color: #22C7D6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        text-decoration: none;
        font-weight: bold;
        border: none;
        cursor: pointer;
        display: inline-block;
        text-align: center;
        width: {'100%' if use_container_width else 'auto'};
    }}
    #{button_id}:hover {{
        background-color: #1aacb8;
    }}
    </style>
    """
    
    dl_link = f'''
    {custom_css}
    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
       download="{filename}" id="{button_id}">
       📥 {button_text}
    </a>
    '''
    
    # Display the download button
    st.markdown(dl_link, unsafe_allow_html=True)
    
    # Add help text if provided
    if help_text:
        st.caption(help_text)
        
    # Add additional guidance for download issues
    st.info("If the download doesn't work, please try right-clicking on the button and select 'Save link as...'")
    
    return excel_data  # Return the binary data in case it's needed elsewhere

def download_dataframe_as_excel(df, sheet_name="Data", filename=None, title="Download Data"):
    """
    Comprehensive function to display a download section with a reliable Excel download button.
    
    Parameters:
    df: DataFrame to export
    sheet_name: Name of the sheet in the Excel file
    filename: Name of the file to download (without extension)
    title: Title for the download section
    """
    st.markdown(f"### {title}")
    
    create_excel_download_button(
        df=df,
        sheet_name=sheet_name,
        filename=filename,
        button_text="Download Excel File",
        help_text="Click to download the data as an Excel file",
        use_container_width=True
    )