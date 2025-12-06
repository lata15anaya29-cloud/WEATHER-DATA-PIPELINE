import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path


# ---------------------------
# SETUP
# ---------------------------

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# List of required scripts
WEATHER_PIPELINE = SCRIPT_DIR / "weather_pipeline.py"
ANALYZE_WEATHER = SCRIPT_DIR / "analyze_weather.py"
WEATHER_DB = SCRIPT_DIR / "weather.db"


# ---------------------------
# FUNCTIONS
# ---------------------------

def run_etl():
    if not WEATHER_PIPELINE.exists():
        messagebox.showerror("Error", f"weather_pipeline.py not found at:\n{WEATHER_PIPELINE}")
        return
    
    try:
        subprocess.run(["python3", str(WEATHER_PIPELINE)], check=True, cwd=SCRIPT_DIR)
        messagebox.showinfo("Success", "Weather data updated successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"ETL failed with exit code {e.returncode}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update data:\n{e}")


def run_graph():
    if not ANALYZE_WEATHER.exists():
        messagebox.showerror("Error", f"analyze_weather.py not found at:\n{ANALYZE_WEATHER}")
        return
    
    try:
        subprocess.run(["python3", str(ANALYZE_WEATHER)], check=True, cwd=SCRIPT_DIR)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Graph failed with exit code {e.returncode}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open graph:\n{e}")


def open_database():
    if not WEATHER_DB.exists():
        messagebox.showerror("Error", f"weather.db not found at:\n{WEATHER_DB}")
        return
    
    try:
        subprocess.Popen(["sqlite3", str(WEATHER_DB)])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open database:\n{e}")


def exit_app():
    root.destroy()


# ---------------------------
# GUI SETUP
# ---------------------------

root = tk.Tk()
root.title("Weather Data Pipeline GUI")
root.geometry("420x300")
root.config(bg="#F5E6CC")   # soft background

title = tk.Label(
    root,
    text="Weather Data Pipeline GUI",
    font=("Arial", 18, "bold"),
    bg="#F5E6CC",
    fg="#4A3F35"
)
title.pack(pady=20)

btn_update = tk.Button(
    root,
    text="Update Weather Data (ETL)",
    font=("Arial", 14),
    bg="#7CA3C2",
    fg="white",
    command=run_etl,
    width=25
)
btn_update.pack(pady=10)

btn_graph = tk.Button(
    root,
    text="Show All Cities Graph",
    font=("Arial", 14),
    bg="#CDB180",
    fg="white",
    command=run_graph,
    width=25
)
btn_graph.pack(pady=10)

btn_db = tk.Button(
    root,
    text="Open Database in Terminal",
    font=("Arial", 14),
    bg="#E1C699",
    fg="white",
    command=open_database,
    width=25
)
btn_db.pack(pady=10)

btn_exit = tk.Button(
    root,
    text="Exit",
    font=("Arial", 14),
    bg="#B56576",
    fg="white",
    command=exit_app,
    width=25
)
btn_exit.pack(pady=10)


root.mainloop()
