import os
import requests
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict

# Your OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var)
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "963b46746c6d8157176bb34b2ae32003")

# Database file name
DB_NAME = "weather.db"

# List of cities to track
CITIES = [
    {"id": 1, "name": "Jalandhar", "country": "IN"},
    {"id": 2, "name": "Meerut", "country": "IN"},
    {"id": 3, "name": "Chandigarh", "country": "IN"},
]


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    # make row access easier if needed
    conn.row_factory = sqlite3.Row
    # enforce foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create required tables (if they don't exist)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                timestamp_utc TEXT NOT NULL,
                temperature_c REAL,
                humidity REAL,
                pressure INTEGER,
                wind_speed REAL,
                weather_main TEXT,
                weather_description TEXT,
                raw_json TEXT,
                FOREIGN KEY(city_id) REFERENCES cities(id),
                UNIQUE(city_id, timestamp_utc) ON CONFLICT IGNORE
            )
            """
        )
        conn.commit()


def save_cities():
    """Ensure the predefined cities are present in the DB."""
    with get_connection() as conn:
        cur = conn.cursor()
        for city in CITIES:
            cur.execute(
                "INSERT OR IGNORE INTO cities (id, name, country) VALUES (?, ?, ?)",
                (city["id"], city["name"], city["country"]),
            )
        conn.commit()


def fetch_weather(city: Dict) -> Optional[Dict]:
    """Fetch current weather JSON from OpenWeatherMap for a city."""
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("OPENWEATHER_API_KEY is not set or is using placeholder. Set env var to fetch real data.")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": f"{city['name']},{city['country']}", "appid": API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"Error fetching weather for {city['name']}: {exc}")
        return None


def transform_weather_json(raw: Dict) -> Optional[Dict]:
    """Return normalized weather data (converted to Celsius and with derived fields)."""
    if not raw:
        return None

    main = raw.get("main", {})
    wind = raw.get("wind", {})
    weather_array = raw.get("weather", [])
    weather_main = None
    weather_description = None
    if weather_array:
        first = weather_array[0]
        weather_main = first.get("main")
        weather_description = first.get("description")

    dt = raw.get("dt")
    if dt:
        timestamp_utc = datetime.utcfromtimestamp(int(dt)).isoformat()
    else:
        timestamp_utc = datetime.utcnow().isoformat()

    temp_k = main.get("temp")
    temp_c = None
    if temp_k is not None:
        try:
            temp_c = float(temp_k) - 273.15
        except (ValueError, TypeError):
            temp_c = None

    feels_like_k = main.get("feels_like")
    feels_like_c = None
    if feels_like_k is not None:
        try:
            feels_like_c = float(feels_like_k) - 273.15
        except (ValueError, TypeError):
            feels_like_c = None

    return {
        "timestamp_utc": timestamp_utc,
        "temperature_c": temp_c,
        "feels_like_c": feels_like_c,
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind_speed": wind.get("speed"),
        "weather_main": weather_main,
        "weather_description": weather_description,
        "raw_json": json.dumps(raw, ensure_ascii=False),
    }


def save_weather(city_id: int, weather: Dict) -> None:
    """Insert one weather row. Duplicate (same city_id + timestamp_utc) will be ignored."""
    if not weather:
        return
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO weather_readings
                    (city_id, timestamp_utc, temperature_c, humidity, pressure, wind_speed, weather_main, weather_description, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    city_id,
                    weather["timestamp_utc"],
                    weather["temperature_c"],
                    weather["humidity"],
                    weather["pressure"],
                    weather["wind_speed"],
                    weather["weather_main"],
                    weather["weather_description"],
                    weather["raw_json"],
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            # e.g., unique constraint conflict or foreign key violation
            print(f"DB integrity error while saving weather for city_id {city_id}: {exc}")
        except Exception as exc:
            print(f"Unexpected DB error while saving weather for city_id {city_id}: {exc}")


def run_etl():
    """Main ETL runner: initialize DB, ensure cities, fetch weather and store results."""
    print("Running Weather ETL...")
    init_db()
    save_cities()

    for city in CITIES:
        print(f"Fetching weather for {city['name']}...")
        raw = fetch_weather(city)
        if not raw:
            print(f"Skipping {city['name']} due to fetch error.")
            continue

        weather = transform_weather_json(raw)
        if weather:
            save_weather(city["id"], weather)
            print(f"Saved weather for {city['name']} ({weather['timestamp_utc']})")
        else:
            print(f"Skipping {city['name']} due to transform error.")

    print("ETL Complete.")


if __name__ == "__main__":
    run_etl()
