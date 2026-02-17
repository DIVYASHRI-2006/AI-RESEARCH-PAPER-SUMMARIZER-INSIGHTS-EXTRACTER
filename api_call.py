# Get request
import requests
url = "https://api.github.com/users/octocat";
response = requests.get(url)
print(response.status_code) # 200 means success, 400 means failure, 500 server error
print(response.json())

# post request
import requests


def get_weather_open_meteo(lat, lon):
    """
    Fetch current + hourly forecast weather data from Open-Meteo
    for the given latitude and longitude.
    """

    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "forecast_days": 1
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    return response.json()


def pretty_print(data):
    if not data:
        return

    # Location details
    print("Location:", data.get("location"))
    print(" Latitude:", data.get("latitude"))
    print(" Longitude:", data.get("longitude"))

    # Current weather
    cw = data.get("current_weather", {})

    print("\nCurrent Weather:")
    print(" Temperature:", cw.get("temperature"), "°C")
    print(" Wind speed:", cw.get("windspeed"), "m/s")
    print(" Wind direction:", cw.get("winddirection"), "°")
    print(" Time:", cw.get("time"))


if __name__ == "__main__":
    # Example: New Delhi (lat=28.6139, lon=77.2090)
    data = get_weather_open_meteo(28.6139, 77.2090)
    pretty_print(data)

