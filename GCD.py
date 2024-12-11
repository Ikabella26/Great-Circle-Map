import streamlit as st
import math
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static

# Haversine formula to calculate the great-circle distance
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  

# Function to calculate the initial and final bearing
def calculate_bearing(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

    initial_bearing = math.atan2(x, y)
    initial_bearing = (math.degrees(initial_bearing) + 360) % 360

    # Final bearing
    final_bearing = (initial_bearing + 180) % 360
    return initial_bearing, final_bearing

# Function to create a map with basemap
def create_map_with_basemap(koordinat1, koordinat2, basemap_style):
    # Create base map centered on midpoint between the two coordinates
    midpoint_lat = (koordinat1[0] + koordinat2[0]) / 2
    midpoint_lon = (koordinat1[1] + koordinat2[1]) / 2
    m = folium.Map(location=[midpoint_lat, midpoint_lon], zoom_start=2)

    # Add basemap style based on user selection
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

    return m

# Streamlit App
st.set_page_config(page_title="Great Circle Distance Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Great Circle Distance Calculator")

# Sidebar for input selection
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

# Geocoder using Geopy
geolocator = Nominatim(user_agent="GreatCircleDistanceApp")

def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

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

# Basemap selection
basemap_style = st.selectbox("🌍 Select Basemap Style", ["Google Maps", "Google Satellite", "Google Terrain", "Esri Satellite"])

# Display results if both coordinates are valid
if koordinat1 and koordinat2:
    jarak_haversine = haversine(koordinat1, koordinat2)
    initial_bearing, final_bearing = calculate_bearing(koordinat1, koordinat2)

    st.markdown("### **:blue[Results:]**")
    st.markdown(f"**<span style='color:teal;'>Haversine Distance:</span>** {jarak_haversine:.2f} km", unsafe_allow_html=True)
    st.markdown(f"**<span style='color:teal;'>Initial Bearing:</span>** {initial_bearing:.2f}°", unsafe_allow_html=True)
    st.markdown(f"**<span style='color:teal;'>Final Bearing:</span>** {final_bearing:.2f}°", unsafe_allow_html=True)

    # Generate map with basemap style
    m = create_map_with_basemap(koordinat1, koordinat2, basemap_style)
    
    # Add markers for the locations
    folium.Marker(location=koordinat1, popup="Location 1").add_to(m)
    folium.Marker(location=koordinat2, popup="Location 2").add_to(m)

    # Display the map in Streamlit
    st.subheader("Map with Selected Basemap")
    folium_static(m)

else:
    st.warning("Please provide valid inputs to calculate coordinates.")
