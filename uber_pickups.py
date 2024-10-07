import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set the title of the Streamlit app
st.title('Uber pickups in NYC')

# Constants
DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# Load data function with caching to improve performance
@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Text to indicate data loading state
data_load_state = st.text('Loading data...')
data = load_data(10000)  # Load 10,000 rows of data
data_load_state.text("Done! (using st.cache_data)")  # Update text when data is loaded

# Show raw data if checkbox is selected
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Pickups by hour of the day
st.subheader('Number of pickups by hour')

# Calculate histogram values for pickups by hour
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24)
)[0]

# Display the histogram as a bar chart
st.bar_chart(hist_values)

# Filter data by hour using a slider
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# Show map for the filtered data by hour
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)

# Analysis 1: Pickups by day of the week
st.subheader('Number of pickups by day of week')

# Add a column for day of the week
data['day_of_week'] = data[DATE_COLUMN].dt.day_name()

# Show bar chart for pickups by day of the week
pickup_counts_by_day = data['day_of_week'].value_counts()
st.bar_chart(pickup_counts_by_day)

# Analysis 2: Heatmap for pickups by day and hour using seaborn
st.subheader('Heatmap of pickups by hour and day')

# Create a pivot table for the heatmap
hour_day_data = data.groupby([data[DATE_COLUMN].dt.day_name(), data[DATE_COLUMN].dt.hour]).size().unstack()

# Convert the pivot table to ensure only numeric data is used
hour_day_data = hour_day_data.fillna(0)  # Replace any NaN values with 0

# Plot the heatmap using seaborn
fig, ax = plt.subplots()
sns.heatmap(hour_day_data, cmap="YlGnBu", ax=ax)

# Display the heatmap in the Streamlit app
st.pyplot(fig)

# Analysis 3: Top 5 pickup locations
st.subheader('Top 5 pickup locations')

# Group by lat and lon to find the top 5 pickup locations
top_locations = data.groupby(['lat', 'lon']).size().reset_index(name='count').sort_values(by='count', ascending=False).head(5)

# Show the top 5 pickup locations as a table
st.write(top_locations)

# Show these locations on a map
st.map(top_locations)

# Analysis 4: Pickups by Date
st.subheader('Pickups by Date')

# Allow the user to filter by date
selected_date = st.date_input('Select a date', data[DATE_COLUMN].min())

# Filter the data by the selected date
filtered_data_by_date = data[data[DATE_COLUMN].dt.date == pd.to_datetime(selected_date).date()]
st.map(filtered_data_by_date)

# Analysis 5: Correlation Analysis (Fix for non-numeric data)
st.subheader('Correlation Analysis')

# Select only numeric columns for correlation analysis
numeric_data = data.select_dtypes(include=['float64', 'int64'])

# Calculate the correlation matrix for numerical columns
correlation_matrix = numeric_data.corr()

# Display the correlation matrix
st.write(correlation_matrix)

# Analysis 6: Interactive Filters by Day and Hour
st.subheader('Filter Data by Day and Hour')

# Select box for day of the week
day_of_week = st.selectbox('Select day of the week', data['day_of_week'].unique())

# Slider for hour
hour = st.slider('Select hour', 0, 23, 12)

# Filter the data based on the selected day and hour
filtered_data_interactive = data[(data['day_of_week'] == day_of_week) & (data[DATE_COLUMN].dt.hour == hour)]

# Show the filtered data on a map
st.map(filtered_data_interactive)
