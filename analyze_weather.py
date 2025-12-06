import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_NAME = "weather.db"


def load_data():
    """Load joined data from SQLite into a pandas DataFrame."""
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            """
            SELECT
                wr.id,
                c.name AS city,
                wr.timestamp_utc,
                wr.temperature_c,
                wr.humidity,
                wr.wind_speed
            FROM weather_readings wr
            JOIN cities c ON wr.city_id = c.id
            ORDER BY wr.timestamp_utc
            """,
            conn,
        )

    if df.empty:
        print("No data found in weather_readings table.")
        return df

    # Convert timestamp to datetime
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
    return df


def plot_temperature_for_city(df: pd.DataFrame, city_name: str) -> None:
    """Plot temperature trend for a single city."""
    if df.empty:
        print("No data to plot.")
        return

    city_df = df[df["city"] == city_name]

    if city_df.empty:
        print(f"No data for city: {city_name}")
        return

    plt.figure()
    plt.plot(city_df["timestamp_utc"], city_df["temperature_c"], marker="o")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Temperature Trend - {city_name}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_humidity_comparison(df: pd.DataFrame) -> None:
    """Plot humidity trends for all cities on one graph."""
    if df.empty:
        print("No data to plot.")
        return

    plt.figure()
    for city, city_df in df.groupby("city"):
        plt.plot(
            city_df["timestamp_utc"],
            city_df["humidity"],
            marker="o",
            label=city,
        )

    plt.xlabel("Time")
    plt.ylabel("Humidity (%)")
    plt.title("Humidity Trend Comparison (All Cities)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_all_cities_temperature(df: pd.DataFrame) -> None:
    """Plot temperature trends for all cities on one graph."""
    if df.empty:
        print("No data to plot.")
        return

    plt.figure()
    for city, city_df in df.groupby("city"):
        plt.plot(
            city_df["timestamp_utc"],
            city_df["temperature_c"],
            marker="o",
            label=city,
        )

    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Trend of All Cities")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data = load_data()
    if data is None or data.empty:
        # If there is no data, just stop here.
        exit()

    # Show some rows in terminal
    print(data.head())

    # 1) Graph for all three cities on one plot
    plot_all_cities_temperature(data)

    # 2) Single-city temperature graph (optional)
    # plot_temperature_for_city(data, "Jalandhar")

    # 3) Humidity comparison graph (optional)
    # plot_humidity_comparison(data)
