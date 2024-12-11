import streamlit as st
import math
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

# Function to get coordinates from a location name
def get_coordinates(location):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(location)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Function to create a map
def create_map(segmen, koordinat1, koordinat2, projection="mercator", basemap_style="osm"):
    fig = go.Figure()

    # Add markers for the locations
    fig.add_trace(go.Scattergeo(
        lon=[koordinat1[1], koordinat2[1]],
        lat=[koordinat1[0], koordinat2[0]],
        mode='markers',
        marker=dict(size=12, color='red'),
        text=['Point 1', 'Point 2']
    ))

    # Add the great circle path
    fig.add_trace(go.Scattergeo(
        lon=[s[1] for s in segmen],
        lat=[s[0] for s in segmen],
        mode='lines',
        line=dict(width=3, color='blue'),
        name="Great Circle Path"
    ))

    # Set basemap style based on input
    if basemap_style == "osm":
        fig.update_layout(
            geo=dict(
                projection_type=projection,
                showland=True,
                landcolor="white",
                subunitcolor="rgb(255, 255, 255)"
            ),
            mapbox=dict(
                style="open-street-map"  # OpenStreetMap style
            )
        )
    elif basemap_style == "esri":
        fig.update_layout(
            geo=dict(
                projection_type=projection,
                showland=True,
                landcolor="white",
                subunitcolor="rgb(255, 255, 255)"
            ),
            mapbox=dict(
                style="esri.WorldImagery"  # ESRI World Imagery basemap
            )
        )

    # Update layout for additional map elements like title and size
    fig.update_layout(
        title="Great Circle Path with Selected Basemap",
        height=800,  # Set the height of the map
        width=1200,  # Set the width of the map
        showlegend=True,
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="black"
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Remove margins around the plot
    )

    return fig

# Streamlit interface

st.title("Great Circle Path Map with Streamlit")

# Input for location names
location1 = st.text_input("Enter the first location", "Jakarta, Indonesia")
location2 = st.text_input("Enter the second location", "New York, USA")

# Get coordinates for both locations
koordinat1 = get_coordinates(location1)
koordinat2 = get_coordinates(location2)

if koordinat1 and koordinat2:
    # Calculate the great circle path (this is a placeholder, replace with actual calculation)
    segmen = [[koordinat1[0], koordinat1[1]], [koordinat2[0], koordinat2[1]]]  # Placeholder segment

    # Dropdown to select basemap style
    basemap_style = st.selectbox("Select Basemap", ["osm", "esri"])

    # Create the map with the selected basemap
    fig = create_map(segmen, koordinat1, koordinat2, basemap_style=basemap_style)

    # Display the map in Streamlit
    st.plotly_chart(fig)

else:
    st.error("Please enter valid location names to get the coordinates.")
