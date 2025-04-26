import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
import os
import uuid
import tempfile
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import write_image
from utils.database import get_quotes_from_db
from utils.excel_export import create_excel_download_button, download_dataframe_as_excel

# Function to create a downloadable chart image directly
def get_chart_as_image(fig):
    """Convert a plotly figure to a PNG image and return as bytes"""
    # Create a BytesIO object
    img_bytes = io.BytesIO()
    
    # Write the figure as a PNG image to the BytesIO object
    fig.write_image(img_bytes, format='png', scale=2)
    
    # Reset the pointer to the beginning of the BytesIO object
    img_bytes.seek(0)
    
    # Return the BytesIO object
    return img_bytes.getvalue()

# Set page title and configure page
st.set_page_config(
    page_title="KMI Services - Business Dashboard",
    page_icon="💧",
    layout="wide"
)

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("static/images/logo.jpg", width=100)
with col2:
    st.title("Business Dashboard")
    st.markdown("Business performance metrics and analytics")

# Admin password protection
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    with st.form("admin_auth_form"):
        st.subheader("Admin Authentication")
        password = st.text_input("Enter admin password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Simple password check - in a real app, use more secure authentication
            if password == "admin123":  # This is a placeholder, use a secure method in production
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")

else:
    # Get quotes data
    try:
        quotes_df = get_quotes_from_db()
        
        if len(quotes_df) == 0:
            st.info("No quotes data available for analysis.")
        else:
            # Convert timestamp to datetime
            quotes_df["timestamp"] = pd.to_datetime(quotes_df["timestamp"])
            
            # Handle cleaning_date conversion more safely
            if "cleaning_date" in quotes_df.columns:
                # First, fill NaN values with a placeholder
                quotes_df["cleaning_date"] = quotes_df["cleaning_date"].fillna("01/01/2000")
                
                # Try to parse dates with various formats
                try:
                    # Try UK format first (DD/MM/YYYY)
                    quotes_df["cleaning_date"] = pd.to_datetime(quotes_df["cleaning_date"], dayfirst=True)
                except Exception as e:
                    # If that fails, try with flexible parser
                    try:
                        quotes_df["cleaning_date"] = pd.to_datetime(quotes_df["cleaning_date"], errors='coerce', dayfirst=True)
                        # Fill any NaT values with a default date
                        quotes_df["cleaning_date"] = quotes_df["cleaning_date"].fillna(pd.Timestamp("2000-01-01"))
                    except Exception as e2:
                        # As a last resort, set all to a default date
                        quotes_df["cleaning_date"] = pd.Timestamp("2000-01-01")
            
            # Add some calculated columns
            quotes_df["month"] = quotes_df["timestamp"].dt.strftime("%Y-%m")
            quotes_df["week"] = quotes_df["timestamp"].dt.strftime("%Y-%U")
            quotes_df["day"] = quotes_df["timestamp"].dt.date
            
            # Date range filter
            st.sidebar.header("Filter Data")
            
            # Get min and max dates
            min_date = quotes_df["timestamp"].min().date()
            max_date = quotes_df["timestamp"].max().date()
            
            # Date range selection with UK format
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(
                    min_date,
                    max_date
                ),
                min_value=min_date,
                max_value=max_date,
                format="DD/MM/YYYY"  # UK date format
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = quotes_df[
                    (quotes_df["timestamp"].dt.date >= start_date) & 
                    (quotes_df["timestamp"].dt.date <= end_date)
                ]
            else:
                filtered_df = quotes_df
            
            # Add region filter
            regions = ["All"] + sorted(quotes_df["region"].unique().tolist())
            selected_region = st.sidebar.selectbox("Select Region", regions)
            
            if selected_region != "All":
                filtered_df = filtered_df[filtered_df["region"] == selected_region]
            
            # Add service type filter
            service_types = ["All"] + sorted(quotes_df["service_type"].unique().tolist())
            selected_service = st.sidebar.selectbox("Select Service Type", service_types)
            
            if selected_service != "All":
                filtered_df = filtered_df[filtered_df["service_type"] == selected_service]
            
            # Add status filter
            statuses = ["All"] + sorted(quotes_df["status"].unique().tolist())
            selected_status = st.sidebar.selectbox("Select Status", statuses)
            
            if selected_status != "All":
                filtered_df = filtered_df[filtered_df["status"] == selected_status]
            
            # Dashboard metrics
            st.header("Key Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_quotes = len(filtered_df)
                st.metric("Total Quotes", total_quotes)
            
            with col2:
                scheduled_quotes = len(filtered_df[filtered_df["status"] == "Scheduled"])
                scheduled_percentage = (scheduled_quotes / total_quotes * 100) if total_quotes > 0 else 0
                st.metric("Scheduled", f"{scheduled_quotes} ({scheduled_percentage:.1f}%)")
            
            with col3:
                completed_quotes = len(filtered_df[filtered_df["status"] == "Completed"])
                completed_percentage = (completed_quotes / total_quotes * 100) if total_quotes > 0 else 0
                st.metric("Completed", f"{completed_quotes} ({completed_percentage:.1f}%)")
            
            with col4:
                total_revenue = filtered_df["total_price"].sum()
                average_quote = filtered_df["total_price"].mean()
                st.metric("Total Revenue", f"£{total_revenue:.2f}", f"Avg: £{average_quote:.2f}")
            
            # Charts
            st.header("Revenue Analysis")
            
            tab1, tab2, tab3 = st.tabs(["Revenue Trends", "Regional Analysis", "Service Type Analysis"])
            
            with tab1:
                # Revenue by time period
                st.subheader("Revenue Trends")
                time_period = st.radio(
                    "Select Time Period",
                    options=["Daily", "Weekly", "Monthly"],
                    horizontal=True
                )
                
                if time_period == "Daily":
                    # Group by day
                    daily_revenue = filtered_df.groupby("day")["total_price"].sum().reset_index()
                    daily_revenue["day"] = pd.to_datetime(daily_revenue["day"])
                    
                    fig = px.line(
                        daily_revenue,
                        x="day",
                        y="total_price",
                        labels={"day": "Date", "total_price": "Revenue (£)"},
                        title="Daily Revenue"
                    )
                    # Enable image export
                    config = {
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',  # one of png, svg, jpeg, webp
                            'filename': 'daily_revenue',
                            'height': 500,
                            'width': 700,
                            'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
                        }
                    }
                    st.plotly_chart(fig, use_container_width=True, config=config)
                    st.info("Click the camera icon in the chart toolbar to download as an image")
                    
                elif time_period == "Weekly":
                    # Group by week
                    weekly_revenue = filtered_df.groupby("week")["total_price"].sum().reset_index()
                    
                    fig = px.bar(
                        weekly_revenue,
                        x="week",
                        y="total_price",
                        labels={"week": "Week", "total_price": "Revenue (£)"},
                        title="Weekly Revenue"
                    )
                    # Enable image export
                    config = {
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'weekly_revenue',
                            'height': 500,
                            'width': 700,
                            'scale': 1
                        }
                    }
                    st.plotly_chart(fig, use_container_width=True, config=config)
                    st.info("Click the camera icon in the chart toolbar to download as an image")
                    
                else:  # Monthly
                    # Group by month
                    monthly_revenue = filtered_df.groupby("month")["total_price"].sum().reset_index()
                    
                    fig = px.bar(
                        monthly_revenue,
                        x="month",
                        y="total_price",
                        labels={"month": "Month", "total_price": "Revenue (£)"},
                        title="Monthly Revenue"
                    )
                    # Enable image export
                    config = {
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'monthly_revenue',
                            'height': 500,
                            'width': 700,
                            'scale': 1
                        }
                    }
                    st.plotly_chart(fig, use_container_width=True, config=config)
                    st.info("Click the camera icon in the chart toolbar to download as an image")
            
            with tab2:
                # Regional analysis
                st.subheader("Revenue by Region")
                
                region_revenue = filtered_df.groupby("region")["total_price"].sum().reset_index()
                region_count = filtered_df.groupby("region").size().reset_index(name="count")
                region_data = pd.merge(region_revenue, region_count, on="region")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        region_data,
                        values="total_price",
                        names="region",
                        title="Revenue Distribution by Region"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        region_data,
                        x="region",
                        y="total_price",
                        color="region",
                        labels={"region": "Region", "total_price": "Revenue (£)"},
                        title="Revenue by Region"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show average price by region
                st.subheader("Average Quote by Region")
                region_avg = filtered_df.groupby("region")["total_price"].mean().reset_index()
                region_avg = region_avg.sort_values("total_price", ascending=False)
                
                fig = px.bar(
                    region_avg,
                    x="region",
                    y="total_price",
                    color="region",
                    labels={"region": "Region", "total_price": "Average Quote (£)"},
                    title="Average Quote Value by Region"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                # Service type analysis
                st.subheader("Revenue by Service Type")
                
                service_revenue = filtered_df.groupby("service_type")["total_price"].sum().reset_index()
                service_count = filtered_df.groupby("service_type").size().reset_index(name="count")
                service_data = pd.merge(service_revenue, service_count, on="service_type")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        service_data,
                        values="total_price",
                        names="service_type",
                        title="Revenue Distribution by Service Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        service_data,
                        x="service_type",
                        y="total_price",
                        color="service_type",
                        labels={"service_type": "Service Type", "total_price": "Revenue (£)"},
                        title="Revenue by Service Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Additional Services Analysis
            st.header("Additional Services Analysis")
            
            # Calculate additional services stats
            total_oven_clean = filtered_df["oven_clean"].sum()
            total_carpet_cleaning = filtered_df["carpet_cleaning"].sum()
            total_internal_windows = filtered_df["internal_windows"].sum()
            total_external_windows = filtered_df["external_windows"].sum()
            total_balcony_patio = filtered_df["balcony_patio"].sum()
            total_cleaning_materials = filtered_df["cleaning_materials"].sum()
            
            # Create a dataframe for the additional services
            additional_services_data = pd.DataFrame({
                "Service": [
                    "Oven Clean", "Carpet Cleaning", "Internal Windows",
                    "External Windows", "Balcony/Patio", "Cleaning Materials"
                ],
                "Count": [
                    total_oven_clean, total_carpet_cleaning, total_internal_windows,
                    total_external_windows, total_balcony_patio, total_cleaning_materials
                ]
            })
            
            fig = px.bar(
                additional_services_data,
                x="Service",
                y="Count",
                color="Service",
                title="Additional Services Popularity"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Referral Source Analysis
            if 'referral_source' in filtered_df.columns:
                st.header("Referral Source Analysis")
                
                # Clean the data by removing None or empty values
                referral_df = filtered_df[filtered_df["referral_source"].notna()]
                referral_df = referral_df[referral_df["referral_source"] != "Please select..."]
                
                if len(referral_df) > 0:
                    referral_counts = referral_df.groupby("referral_source").size().reset_index(name="count")
                    referral_revenue = referral_df.groupby("referral_source")["total_price"].sum().reset_index()
                    referral_data = pd.merge(referral_counts, referral_revenue, on="referral_source")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.pie(
                            referral_data,
                            values="count",
                            names="referral_source",
                            title="Quote Distribution by Referral Source"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(
                            referral_data,
                            x="referral_source",
                            y="total_price",
                            color="referral_source",
                            labels={"referral_source": "Referral Source", "total_price": "Revenue (£)"},
                            title="Revenue by Referral Source"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Show "Other" referral sources if available
                    other_referrals = referral_df[referral_df["referral_source"] == "Other"]
                    if len(other_referrals) > 0 and "referral_other" in other_referrals.columns:
                        other_referrals = other_referrals[other_referrals["referral_other"].notna()]
                        if len(other_referrals) > 0:
                            st.subheader("Details of 'Other' Referral Sources")
                            st.dataframe(
                                other_referrals[["customer_name", "referral_other", "total_price"]],
                                hide_index=True
                            )
                else:
                    st.info("No referral source data available for analysis.")
            
            # Raw Data
            st.header("Detailed Quote Data")
            with st.expander("View Raw Data"):
                # Format the data for display
                display_df = filtered_df.copy()
                
                # Convert boolean columns to more readable Yes/No
                for col in ["oven_clean", "carpet_cleaning", "internal_windows", "external_windows", 
                            "balcony_patio", "cleaning_materials", "sent_to_customer", "admin_created"]:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: "Yes" if x else "No")
                
                # Format timestamp for better readability (UK format)
                if "timestamp" in display_df.columns:
                    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
                
                # Format dates in UK format
                if "cleaning_date" in display_df.columns:
                    display_df["cleaning_date"] = display_df["cleaning_date"].dt.strftime("%d/%m/%Y")
                
                # Format price columns
                for col in ["base_price", "total_price", "markup", "hourly_rate", 
                           "extra_bathrooms_cost", "extra_reception_cost", "additional_services_cost", "materials_cost"]:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"£{x:.2f}" if pd.notnull(x) else "")
                
                # Format hours required
                if "hours_required" in display_df.columns:
                    display_df["hours_required"] = display_df["hours_required"].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
                
                # Show all available columns with frozen headers
                st.dataframe(
                    display_df, 
                    hide_index=True, 
                    use_container_width=True,
                    height=400,  # Fixed height to enable vertical scrolling
                    column_config={col: st.column_config.Column(col) for col in display_df.columns}  # Ensure column headers are visible
                )
                
                # Add Excel download button for the dashboard data
                excel_file = io.BytesIO()
                with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
                    # Create full export with all columns
                    filtered_df.to_excel(writer, sheet_name="Dashboard Data", index=False)
                    
                    # Add a summary sheet
                    summary_data = {
                        "Metric": [
                            "Total Quotes", 
                            "Scheduled Quotes", 
                            "Completed Quotes", 
                            "Total Revenue", 
                            "Average Quote Value"
                        ],
                        "Value": [
                            total_quotes,
                            scheduled_quotes,
                            completed_quotes,
                            f"£{total_revenue:.2f}",
                            f"£{average_quote:.2f}"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
                    
                    # Add formatting
                    workbook = writer.book
                    
                    # Format the main data sheet
                    worksheet = writer.sheets["Dashboard Data"]
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#22C7D6', 'color': 'white'})
                    for col_num, value in enumerate(filtered_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Format the summary sheet
                    summary_sheet = writer.sheets["Summary"]
                    summary_sheet.set_column('A:A', 25)
                    summary_sheet.set_column('B:B', 20)
                    for col_num, value in enumerate(summary_data["Metric"]):
                        summary_sheet.write(col_num+1, 0, value)
                        summary_sheet.write(col_num+1, 1, summary_data["Value"][col_num])
                    
                    # Write headers with format
                    for col_num, value in enumerate(summary_data.keys()):
                        summary_sheet.write(0, col_num, value, header_format)
                
                excel_file.seek(0)
                
                # Improved Excel export approach
                st.markdown("### Export Dashboard Data")
                
                # Display the full table with a fixed height so it doesn't overwhelm the page
                st.dataframe(filtered_df, height=400, use_container_width=True)
                
                # Create Excel file in memory
                from io import BytesIO
                output = BytesIO()
                
                # Generate timestamp for unique filename
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Create an Excel workbook with worksheets for data and summary
                import xlsxwriter
                workbook = xlsxwriter.Workbook(output)
                
                # Add data worksheet
                data_sheet = workbook.add_worksheet("Dashboard Data")
                
                # Add headers
                for col_num, column_title in enumerate(filtered_df.columns):
                    data_sheet.write(0, col_num, column_title)
                
                # Add data rows with NaN/INF handling
                for row_num, row in enumerate(filtered_df.values):
                    for col_num, cell_value in enumerate(row):
                        # Handle NaN, INF and other problematic values
                        if cell_value is None or (isinstance(cell_value, float) and (pd.isna(cell_value) or cell_value == float('inf') or cell_value == float('-inf'))):
                            data_sheet.write(row_num + 1, col_num, "")  # Write empty string instead
                        else:
                            try:
                                data_sheet.write(row_num + 1, col_num, cell_value)
                            except:
                                # If any other error, convert to string
                                data_sheet.write(row_num + 1, col_num, str(cell_value))
                
                # Add summary worksheet
                summary_sheet = workbook.add_worksheet("Summary")
                
                # Write summary data
                summary_data = [
                    ["Total Quotes", total_quotes],
                    ["Scheduled Quotes", scheduled_quotes],
                    ["Completed Quotes", completed_quotes],
                    ["Total Revenue", total_revenue],
                    ["Average Quote Value", average_quote]
                ]
                
                for row_num, row_data in enumerate(summary_data):
                    for col_num, cell_value in enumerate(row_data):
                        # Handle NaN, INF and other problematic values
                        if cell_value is None or (isinstance(cell_value, float) and (pd.isna(cell_value) or cell_value == float('inf') or cell_value == float('-inf'))):
                            summary_sheet.write(row_num, col_num, "")  # Write empty string instead
                        else:
                            try:
                                summary_sheet.write(row_num, col_num, cell_value)
                            except:
                                # If any other error, convert to string
                                summary_sheet.write(row_num, col_num, str(cell_value))
                
                # Add charts worksheet
                charts_sheet = workbook.add_worksheet("Charts Information")
                
                # Write chart info (since we can't embed interactive charts)
                charts_sheet.write(0, 0, "Important Note About Charts")
                charts_sheet.write(1, 0, "The interactive charts cannot be embedded directly in Excel.")
                charts_sheet.write(2, 0, "Instead, the chart data is included in separate worksheets below.")
                
                # Create worksheets with the chart data
                
                # Region data
                region_chart_sheet = workbook.add_worksheet("Region Chart Data")
                region_chart_sheet.write(0, 0, "Region")
                region_chart_sheet.write(0, 1, "Count")
                region_chart_sheet.write(0, 2, "Revenue")
                
                if 'region' in filtered_df.columns:
                    region_data = filtered_df.groupby("region").agg({
                        "quote_id": "count", 
                        "total_price": "sum"
                    }).reset_index()
                    
                    for row_num, (region, count, revenue) in enumerate(
                        zip(region_data["region"], region_data["quote_id"], region_data["total_price"])
                    ):
                        # Handle region safely
                        if pd.isna(region) or region is None:
                            region_value = "Unknown"
                        else:
                            region_value = str(region)
                            
                        # Handle count and revenue safely
                        if count is None or (isinstance(count, float) and (pd.isna(count) or count == float('inf') or count == float('-inf'))):
                            count_value = 0
                        else:
                            count_value = count
                            
                        if revenue is None or (isinstance(revenue, float) and (pd.isna(revenue) or revenue == float('inf') or revenue == float('-inf'))):
                            revenue_value = 0
                        else:
                            revenue_value = revenue
                            
                        # Write values safely
                        region_chart_sheet.write(row_num + 1, 0, region_value)
                        region_chart_sheet.write(row_num + 1, 1, count_value)
                        region_chart_sheet.write(row_num + 1, 2, revenue_value)
                
                # Service type data
                service_chart_sheet = workbook.add_worksheet("Service Type Chart Data")
                service_chart_sheet.write(0, 0, "Service Type")
                service_chart_sheet.write(0, 1, "Count")
                service_chart_sheet.write(0, 2, "Revenue")
                
                if 'service_type' in filtered_df.columns:
                    service_data = filtered_df.groupby("service_type").agg({
                        "quote_id": "count", 
                        "total_price": "sum"
                    }).reset_index()
                    
                    for row_num, (service, count, revenue) in enumerate(
                        zip(service_data["service_type"], service_data["quote_id"], service_data["total_price"])
                    ):
                        # Handle service safely
                        if pd.isna(service) or service is None:
                            service_value = "Unknown"
                        else:
                            service_value = str(service)
                            
                        # Handle count and revenue safely
                        if count is None or (isinstance(count, float) and (pd.isna(count) or count == float('inf') or count == float('-inf'))):
                            count_value = 0
                        else:
                            count_value = count
                            
                        if revenue is None or (isinstance(revenue, float) and (pd.isna(revenue) or revenue == float('inf') or revenue == float('-inf'))):
                            revenue_value = 0
                        else:
                            revenue_value = revenue
                            
                        # Write values safely
                        service_chart_sheet.write(row_num + 1, 0, service_value)
                        service_chart_sheet.write(row_num + 1, 1, count_value)
                        service_chart_sheet.write(row_num + 1, 2, revenue_value)
                
                # Add regional data
                region_sheet = workbook.add_worksheet("Region Analysis")
                region_sheet.write(0, 0, "Region")
                region_sheet.write(0, 1, "Count")
                region_sheet.write(0, 2, "Revenue")
                
                region_data = filtered_df.groupby("region").agg(
                    {"quote_id": "count", "total_price": "sum"}
                ).reset_index()
                
                for row_num, (region, count, revenue) in enumerate(
                    zip(region_data["region"], region_data["quote_id"], region_data["total_price"])
                ):
                    # Handle region safely
                    if pd.isna(region) or region is None:
                        region_value = "Unknown"
                    else:
                        region_value = str(region)
                        
                    # Handle count and revenue safely
                    if count is None or (isinstance(count, float) and (pd.isna(count) or count == float('inf') or count == float('-inf'))):
                        count_value = 0
                    else:
                        count_value = count
                        
                    if revenue is None or (isinstance(revenue, float) and (pd.isna(revenue) or revenue == float('inf') or revenue == float('-inf'))):
                        revenue_value = 0
                    else:
                        revenue_value = revenue
                        
                    # Write values safely
                    region_sheet.write(row_num + 1, 0, region_value)
                    region_sheet.write(row_num + 1, 1, count_value)
                    region_sheet.write(row_num + 1, 2, revenue_value)
                
                # Add service type data
                service_sheet = workbook.add_worksheet("Service Analysis")
                service_sheet.write(0, 0, "Service Type")
                service_sheet.write(0, 1, "Count")
                service_sheet.write(0, 2, "Revenue")
                
                service_data = filtered_df.groupby("service_type").agg(
                    {"quote_id": "count", "total_price": "sum"}
                ).reset_index()
                
                for row_num, (service, count, revenue) in enumerate(
                    zip(service_data["service_type"], service_data["quote_id"], service_data["total_price"])
                ):
                    # Handle service safely
                    if pd.isna(service) or service is None:
                        service_value = "Unknown"
                    else:
                        service_value = str(service)
                        
                    # Handle count and revenue safely
                    if count is None or (isinstance(count, float) and (pd.isna(count) or count == float('inf') or count == float('-inf'))):
                        count_value = 0
                    else:
                        count_value = count
                        
                    if revenue is None or (isinstance(revenue, float) and (pd.isna(revenue) or revenue == float('inf') or revenue == float('-inf'))):
                        revenue_value = 0
                    else:
                        revenue_value = revenue
                        
                    # Write values safely
                    service_sheet.write(row_num + 1, 0, service_value)
                    service_sheet.write(row_num + 1, 1, count_value)
                    service_sheet.write(row_num + 1, 2, revenue_value)
                
                # Close the workbook to write the content to the BytesIO object
                workbook.close()
                
                # Create a simpler CSV approach that's more reliable
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                
                # Use Streamlit's download button with CSV data
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv_data,
                    file_name="KMI_Dashboard_Data.csv",
                    mime="text/csv"
                )
                
                st.info("""
                **CSV Download Instructions:**
                1. Click the 'Download CSV Report' button above to download the dashboard data
                2. The CSV file can be opened in Excel, Google Sheets, or any spreadsheet program
                3. For the charts, use the camera icons on each chart to download them individually
                4. For more detailed analysis, you can use the text export below to copy and paste into Excel
                """)
                
                # Alternative CSV approach
                st.markdown("#### Alternative: Copy-Paste CSV Data")
                
                # Create CSV data
                csv_string = filtered_df.to_csv(index=False)
                
                # Display CSV in a text area with minimum styling for easy selection
                st.text_area(
                    "Or select this text (Ctrl+A), then copy (Ctrl+C) to paste into Excel:",
                    csv_string,
                    height=200
                )
    
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()