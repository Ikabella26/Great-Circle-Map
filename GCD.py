import streamlit as st
import folium
import math
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

# Fungsi untuk menghitung jarak menggunakan rumus Haversine
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371  # Radius bumi dalam kilometer
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Fungsi untuk menghitung jalur Great Circle (garis melengkung)
def calculate_great_circle_path(coord1, coord2, num_points=100):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    points = []
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_sigma = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))
    
    for i in range(num_points):
        A = math.sin((1 - i / (num_points - 1)) * delta_sigma) / math.sin(delta_sigma)
        B = math.sin(i / (num_points - 1) * delta_sigma) / math.sin(delta_sigma)
        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)

        lat = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
        lon = math.atan2(y, x)
        points.append([math.degrees(lat), math.degrees(lon)])
    
    return points

# Fungsi untuk membuat peta Folium dengan garis melengkung
def create_folium_map(koordinat1, koordinat2, basemap="OpenStreetMap"):
    m = folium.Map(location=[(koordinat1[0] + koordinat2[0]) / 2, (koordinat1[1] + koordinat2[1]) / 2],
                   zoom_start=3, tiles=basemap)

    # Menambahkan marker untuk kedua titik
    folium.Marker(location=koordinat1, popup="Point 1").add_to(m)
    folium.Marker(location=koordinat2, popup="Point 2").add_to(m)

    # Menghitung jalur great-circle
    great_circle = folium.PolyLine(locations=calculate_great_circle_path(koordinat1, koordinat2, num_points=100),
                                   color="blue", weight=2, opacity=0.6)
    great_circle.add_to(m)

    return m

# Fungsi untuk membuat peta Plotly dengan proyeksi Orthographic
def create_plotly_map(koordinat1, koordinat2):
    fig = go.Figure(go.Scattergeo(
        lon=[koordinat1[1], koordinat2[1]],
        lat=[koordinat1[0], koordinat2[0]],
        mode='markers+lines',
        line=dict(width=2, color='blue')
    ))

    fig.update_geos(projection_type="orthographic", 
                   center=dict(lat=(koordinat1[0]+koordinat2[0])/2, lon=(koordinat1[1]+koordinat2[1])/2))

    fig.update_layout(title="Great Circle Path",
                      geo=dict(showland=True, landcolor="lightgray"))

    return fig

# Streamlit app configuration
st.set_page_config(page_title="Great Circle Distance Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Great Circle Distance Calculator")

# Sidebar untuk memilih input
input_method = st.sidebar.selectbox("🔽 Select Input Method", ["Location Names", "Manual Coordinates"])

# Geocoder menggunakan Geopy
geolocator = Nominatim(user_agent="GreatCircleDistanceApp")

def get_coordinates(location_name):
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        st.warning(f"Could not find coordinates for {location_name}.")
        return None

# Variabel koordinat
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

# Tampilkan hasil jika kedua koordinat valid
if koordinat1 and koordinat2:
    jarak_haversine = haversine(koordinat1, koordinat2)

    st.markdown("### **:blue[Results:]**")
    st.markdown(f"**<span style='color:teal;'>Haversine Distance:</span>** {jarak_haversine:.2f} km", unsafe_allow_html=True)

    # Menampilkan peta dengan Folium
    basemap = st.selectbox("🌐 Select Basemap", ["OpenStreetMap", "Stamen Terrain", "Stamen Toner"])
    folium_map = create_folium_map(koordinat1, koordinat2, basemap=basemap)
    folium_static(folium_map)

    # Menampilkan peta dengan Plotly
    plotly_map = create_plotly_map(koordinat1, koordinat2)
    st.plotly_chart(plotly_map, use_container_width=True)
else:
    st.warning("Please provide valid inputs to calculate coordinates.")
