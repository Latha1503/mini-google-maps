# Mini Google Maps – Shortest Route Finder

## Project Overview
A Python-based web application that finds the shortest driving route between two geographical locations and displays it on an interactive map.

## Features
- Enter starting location and destination.
- Convert place names into geographical coordinates.
- Find alternative driving routes.
- Select the shortest route based on distance.
- Display estimated travel time.
- Visualize routes using an interactive map.

## Technologies Used
- Python
- Streamlit
- HeiGIT OpenRouteService API
- Requests
- Folium
- OpenStreetMap
- Python-dotenv

## Project Workflow
1. User enters two locations.
2. Geocoding API converts locations into coordinates.
3. Directions API generates alternative routes.
4. Python selects the shortest returned route.
5. Folium displays the routes on an interactive map.

## How to Run

1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file and add your API key:

   `ORS_API_KEY=your_api_key`

4. Run the application:

   `streamlit run app.py`

## Learning Outcomes
- Python application development
- API integration
- JSON response handling
- Geocoding and geographical coordinates
- Interactive map visualization