import pydeck as pdk
import streamlit as st

from flight_planner import FlightPlanner

if "input_count" not in st.session_state:
    st.session_state.input_count = 1


def on_city_name_change(input_index: int):
    if input_index != st.session_state.input_count - 1:
        return

    st.session_state.input_count += 1


for i in range(st.session_state.input_count):
    st.text_input(
        "City Name", key=f"city_name{i}", on_change=on_city_name_change, args=(i,)
    )

if st.button("Generate flight plan"):
    city_names = list(
        map(
            lambda index: st.session_state[f"city_name{index}"],
            range(st.session_state.input_count - 1),
        )
    )

    flight_planner = FlightPlanner(city_names)
    city_locations = flight_planner.get_cities()
    flight_path = flight_planner.get_flight_path()

    st.pydeck_chart(
        pdk.Deck(
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=city_locations,
                    get_position="[lon, lat]",
                    radius_min_pixels=5,
                    get_color="[200, 30, 0, 160]",
                ),
                pdk.Layer(
                    "PathLayer",
                    data=flight_path,
                    width_scale=20,
                    width_min_pixels=2,
                    get_path="path",
                    get_width=5,
                    get_color="[0, 255, 0, 160]",
                ),
            ]
        )
    )
