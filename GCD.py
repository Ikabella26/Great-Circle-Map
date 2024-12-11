import streamlit as st
import folium
from geopy.geocoders import Nominatim

# Function to get coordinates from location name
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="GreatCircleDistanceApp")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

# Streamlit App
st.set_page_config(page_title="Great Circle Distance Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Great Circle Distance Calculator")

# Sidebar for input selection
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

# Coordinates variables
koordinat1 = None
koordinat2 = None

if input_method == "Location Names":
    location_1_name = st.sidebar.text_input("📍 Location Name 1", "Jakarta, Indonesia")
    location_2_name = st.sidebar.text_input("📍 Location Name 2", "New York, USA")

    koordinat1 = get_coordinates(location_1_name)
    koordinat2 = get_coordinates(location_2_name)

elif input_method == "Manual Coordinates":
    lat1 = st.sidebar.number_input("📍 Latitude of Location 1", value=-6.2)
    lon1 = st.sidebar.number_input("📍 Longitude of Location 1", value=106.816666)
    lat2 = st.sidebar.number_input("📍 Latitude of Location 2", value=40.712776)
    lon2 = st.sidebar.number_input("📍 Longitude of Location 2", value=-74.005974)
    koordinat1 = (lat1, lon1)
    koordinat2 = (lat2, lon2)

# Select basemap style
basemap_style = st.selectbox("🌍 Select Basemap Style", ["Google Maps", "Google Satellite", "Google Terrain", "Esri Satellite"])

# Create Folium map centered on midpoint between two locations
if koordinat1 and koordinat2:
    midpoint_lat = (koordinat1[0] + koordinat2[0]) / 2
    midpoint_lon = (koordinat1[1] + koordinat2[1]) / 2
    
    m = folium.Map(location=[midpoint_lat, midpoint_lon], zoom_start=2)

    # Add Google or Esri layer based on selection
    if basemap_style == "Google Maps":
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps',
            overlay=True,
            control=True
        ).add_to(m)
    
    elif basemap_style == "Google Satellite":
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            overlay=True,
            control=True
        ).add_to(m)
    
    elif basemap_style == "Google Terrain":
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Terrain',
            overlay=True,
            control=True
        ).add_to(m)

    elif basemap_style == "Esri Satellite":
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Satellite',
            overlay=True,
            control=True
        ).add_to(m)

    # Add markers for the locations
    folium.Marker(location=koordinat1, popup="Location 1").add_to(m)
    folium.Marker(location=koordinat2, popup="Location 2").add_to(m)

    # Display the map in Streamlit
    st.subheader("Map with Selected Basemap")
    st.markdown("### **Interactive Map**")
    folium_static(m)
