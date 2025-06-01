import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pyarrow.parquet as pq
import os
import pyarrow.dataset as ds

st.title("Netflix Streaming Analytics Dashboard")

# Configure S3 connection
def configure_s3():
    import boto3
    from botocore.client import Config
    
    # Configure MinIO client
    s3 = boto3.client('s3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        config=Config(signature_version='s3v4')
    )
    return s3

# Load latest data from MinIO
def load_latest_data():
    try:
        # Get the latest partition
        s3 = configure_s3()
        data_path = "s3a://data-lake/processed/analytics"
        
        # List all partitions
        partitions = []
        for obj in s3.list_objects(Bucket='data-lake', Prefix='processed/analytics/year=')['Contents']:
            if obj['Key'].endswith('.parquet'):
                partitions.append(obj['Key'])
        
        if not partitions:
            return pd.DataFrame()
            
        # Read the latest partition
        latest_partition = max(partitions)
        df = pd.read_parquet(f"s3a://{latest_partition}")
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data
data = load_latest_data()

if not data.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_country = st.sidebar.selectbox("Country", data['country'].unique())
    selected_device = st.sidebar.selectbox("Device", data['device'].unique())
    
    filtered_data = data
    if selected_country != "All":
        filtered_data = filtered_data[filtered_data['country'] == selected_country]
    if selected_device != "All":
        filtered_data = filtered_data[filtered_data['device'] == selected_device]
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_data)
    
    # Show user activity metrics
    st.subheader("User Activity Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Views", filtered_data['total_views'].sum())
    
    with col2:
        st.metric("Total Duration (hours)", round(filtered_data['total_duration'].sum() / 3600, 2))
    
    with col3:
        st.metric("Avg Rating", round(filtered_data['avg_rating'].mean(), 2))
    
    with col4:
        st.metric("Watchlist Adds", filtered_data['watchlist_count'].sum())
    
    # Show action distribution by country
    st.subheader("View Distribution by Country")
    country_data = filtered_data.groupby('country')['total_views'].sum().reset_index()
    fig = px.bar(country_data, x='country', y='total_views', title='Views by Country')
    st.plotly_chart(fig)
    
    # Show device distribution
    st.subheader("View Distribution by Device")
    device_data = filtered_data.groupby('device')['total_views'].sum().reset_index()
    fig = px.pie(device_data, names='device', values='total_views', title='Views by Device')
    st.plotly_chart(fig)
    
    # Show top movies by views
    st.subheader("Top Movies by Views")
    top_movies = filtered_data.sort_values('total_views', ascending=False).head(10)
    fig = px.bar(top_movies, x='movie_id', y='total_views', 
               hover_data=['avg_rating', 'watchlist_count'],
               title='Top Movies by Views')
    st.plotly_chart(fig)
    
    # Show rating distribution
    st.subheader("Rating Distribution")
    fig = px.histogram(filtered_data, x='avg_rating', nbins=5,
                      title='Average Rating Distribution')
    st.plotly_chart(fig)
    
    # Show watchlist trends
    st.subheader("Watchlist Trends")
    fig = px.scatter(filtered_data, x='avg_rating', y='watchlist_count',
                    size='total_views', color='country',
                    title='Watchlist Adds vs Ratings')
    st.plotly_chart(fig)
    
    # Show engagement metrics
    st.subheader("Engagement Metrics")
    engagement_data = filtered_data.groupby('country').agg({
        'total_views': 'sum',
        'total_duration': 'sum',
        'avg_rating': 'mean',
        'watchlist_count': 'sum'
    }).reset_index()
    
    fig = px.scatter(engagement_data, x='avg_rating', y='total_views',
                    size='watchlist_count', color='country',
                    title='Country Engagement')
    st.plotly_chart(fig)
    
else:
    st.warning("No data available. Please check if the data pipeline is running.")
    st.info("Make sure Kafka producer and Spark streaming processor are running.")