from collections import defaultdict

import osmnx
import osmnx.distance
import pandas as pd


class FlightPlanner:
    def __init__(self, city_names: list[str]) -> None:
        city_locations = list(map(osmnx.geocode, city_names))
        latitudes, longitudes = zip(*city_locations)

        self.cities = pd.DataFrame({"lat": latitudes, "lon": longitudes})
        self.flight_path = self._calculate_flight_path()

    def get_cities(self) -> pd.DataFrame:
        return self.cities.copy(deep=True)

    def get_flight_path(self):
        return pd.DataFrame(
            {
                "path": [
                    [
                        (self.cities.iloc[index]["lon"], self.cities.iloc[index]["lat"])
                        for index in self.flight_path
                    ]
                ]
            }
        )

    def _calculate_flight_path(self):
        flight_distance = defaultdict(dict)

        for index1, city1 in self.cities.iterrows():
            for index2, city2 in self.cities.iterrows():
                distance = osmnx.distance.great_circle(
                    city1["lat"], city1["lon"], city2["lat"], city2["lon"]
                )

                flight_distance[index1][index2] = distance
                flight_distance[index2][index1] = distance

        _, flight_path = self._knapsack(
            0, set(range(1, len(self.cities))), flight_distance, [0]
        )
        return flight_path

    def _knapsack(
        self,
        current_city: int,
        remaining_cities: set[int],
        flight_distance: dict[int, dict[int, float]],
        flight_path: list[int],
    ) -> tuple[float, list[int]]:
        if not remaining_cities:
            return 0, flight_path

        shortest_distance = float("inf")
        shortest_path = []

        for city_index in remaining_cities:
            new_flight_path = flight_path + [city_index]
            new_remaining_cities = remaining_cities - {city_index}

            distance, updated_flight_path = self._knapsack(
                city_index, new_remaining_cities, flight_distance, new_flight_path
            )
            distance += flight_distance[current_city][city_index]

            if distance < shortest_distance:
                shortest_distance = distance
                shortest_path = updated_flight_path

        return shortest_distance, shortest_path
