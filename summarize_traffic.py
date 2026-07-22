import json
import os

INPUT_FILE = "traffic_history.json"

def analyze_traffic(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'. Make sure the file exists in this directory.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract views data
    views_data = data.get("views", {})
    total_views = sum(day["count"] for day in views_data.values())
    unique_views = sum(day["uniques"] for day in views_data.values())

    # Extract clones data
    clones_data = data.get("clones", {})
    total_clones = sum(day["count"] for day in clones_data.values())
    unique_clones = sum(day["uniques"] for day in clones_data.values())

    # Print summary
    print("=" * 35)
    print("    LIFETIME TRAFFIC SUMMARY    ")
    print("=" * 35)
    print(f"Total Views:       {total_views:,}")
    print(f"Unique Views:      {unique_views:,}")
    print("-" * 35)
    print(f"Total Clones:      {total_clones:,}")
    print(f"Unique Cloners:    {unique_clones:,}")
    print("=" * 35)

if __name__ == "__main__":
    analyze_traffic(INPUT_FILE)