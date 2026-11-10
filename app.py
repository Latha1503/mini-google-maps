
import os
import requests
import streamlit as st
import folium

from dotenv import load_dotenv
from streamlit_folium import st_folium


# 1. Load API key
load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")

# New HeiGIT API endpoints
GEOCODE_URL = "https://api.heigit.org/pelias/v1/search"
ROUTE_URL = "https://api.heigit.org/openrouteservice/v2/directions/driving-car/geojson"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}


# 2. Streamlit page
st.set_page_config(
    page_title="Mini Maps",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Mini Google Maps")
st.write("Find the shortest distance between two places")

if not API_KEY:
    st.error("API key missing. Check your .env file.")
    st.stop()


# 3. Convert place name into coordinates
def get_coordinates(place):

    response = requests.get(
        GEOCODE_URL,
        headers=HEADERS,
        params={
            "text": place,
            "boundary.country": "IND",
            "size": 1
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        raise ValueError(f"Location not found: {place}")

    return features[0]["geometry"]["coordinates"]


# 4. Get alternative routes
def get_routes(start, destination):

    payload = {
        "coordinates": [start, destination],
        "units": "km",
        "alternative_routes": {
            "target_count": 3,
            "weight_factor": 1.4,
            "share_factor": 0.6
        }
    }

    response = requests.post(
        ROUTE_URL,
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json().get("features", [])


# 5. Find shortest route
def find_shortest_route(routes):

    return min(
        routes,
        key=lambda route: route["properties"]["summary"]["distance"]
    )


# 6. Display map
def display_map(start, end, routes, shortest):

    center = [
        (start[1] + end[1]) / 2,
        (start[0] + end[0]) / 2
    ]

    map_object = folium.Map(
        location=center,
        zoom_start=12
    )

    folium.Marker(
        [start[1], start[0]],
        popup="Starting Location",
        icon=folium.Icon(color="green")
    ).add_to(map_object)

    folium.Marker(
        [end[1], end[0]],
        popup="Destination",
        icon=folium.Icon(color="red")
    ).add_to(map_object)

    all_points = []

    for index, route in enumerate(routes):

        distance = route["properties"]["summary"]["distance"]

        is_shortest = route is shortest

        locations = [
            [point[1], point[0]]
            for point in route["geometry"]["coordinates"]
        ]

        all_points.extend(locations)

        folium.PolyLine(
            locations=locations,
            color="green" if is_shortest else "blue",
            weight=7 if is_shortest else 4,
            tooltip=f"Route {index + 1}: {distance:.2f} km"
        ).add_to(map_object)

    if all_points:
        map_object.fit_bounds(all_points)

    st_folium(
        map_object,
        use_container_width=True,
        height=500
    )


# 7. User input

# 7. Store results between Streamlit reruns

if "route_data" not in st.session_state:
    st.session_state.route_data = None


# 8. User input

col1, col2 = st.columns(2)

with col1:
    source = st.text_input(
        "Starting Location",
        placeholder="Gachibowli, Hyderabad"
    )

with col2:
    destination = st.text_input(
        "Destination",
        placeholder="Charminar, Hyderabad"
    )


# 9. Find shortest route

if st.button("Find Shortest Route", type="primary"):

    if not source.strip() or not destination.strip():

        st.warning("Enter both locations.")

    elif source.strip().casefold() == destination.strip().casefold():

        st.warning("Enter two different locations.")

    else:

        try:

            with st.spinner("Finding routes..."):

                start = get_coordinates(source)
                end = get_coordinates(destination)

                routes = get_routes(start, end)

                if not routes:
                    raise ValueError("No routes found.")

                shortest = find_shortest_route(routes)

                # Save results
                st.session_state.route_data = {
                    "start": start,
                    "end": end,
                    "routes": routes,
                    "shortest": shortest
                }

        except Exception as error:

            st.session_state.route_data = None
            st.error(f"Error: {error}")


# 10. Display saved results

if st.session_state.route_data:

    data = st.session_state.route_data

    start = data["start"]
    end = data["end"]
    routes = data["routes"]
    shortest = data["shortest"]

    summary = shortest["properties"]["summary"]

    st.success("Routes found successfully!")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Shortest Distance",
        f"{summary['distance']:.2f} km"
    )

    c2.metric(
        "Estimated Time",
        f"{summary['duration'] / 60:.0f} minutes"
    )

    c3.metric(
        "Routes Found",
        len(routes)
    )

    st.subheader("🗺️ Route Map")

    display_map(start, end, routes, shortest)

    st.subheader("📊 Route Comparison")

    for index, route in enumerate(routes):

        details = route["properties"]["summary"]

        distance = details["distance"]
        duration = details["duration"]

        if route is shortest:

            st.success(
                f"Route {index + 1} - SHORTEST: "
                f"{distance:.2f} km | "
                f"{duration / 60:.0f} minutes"
            )

        else:

            st.info(
                f"Route {index + 1}: "
                f"{distance:.2f} km | "
                f"{duration / 60:.0f} minutes"
            )
