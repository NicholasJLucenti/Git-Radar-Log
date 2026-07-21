import os
import json
import requests
from datetime import datetime

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TARGET_REPO_OWNER = "NicholasJLucenti"
TARGET_REPO_NAME = "Data-Analytics"
OUTPUT_FILE = "traffic_history.json"

if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BASE_URL = f"https://api.github.com/repos/{TARGET_REPO_OWNER}/{TARGET_REPO_NAME}"

def fetch_api(endpoint: str) -> dict | list:
    url = f"{BASE_URL}/{endpoint}" if endpoint else BASE_URL
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def load_history() -> dict:
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {
        "views": {},
        "clones": {},
        "top_referrers": {},
        "popular_paths": {},
        "repository_stats": {}
    }

def merge_time_series(existing: dict, new_entries: list) -> dict:
    """Merges daily traffic metrics (views/clones) and keeps dates sorted chronologically."""
    for entry in new_entries:
        date_str = entry["timestamp"].split("T")[0]
        existing[date_str] = {
            "count": entry["count"],
            "uniques": entry["uniques"]
        }
    return dict(sorted(existing.items()))

def main():
    print(f"Fetching complete activity metrics for {TARGET_REPO_OWNER}/{TARGET_REPO_NAME}...")
    
    # 1. Fetch raw API responses
    views_resp = fetch_api("traffic/views")
    clones_resp = fetch_api("traffic/clones")
    referrers_resp = fetch_api("traffic/popular/referrers")
    paths_resp = fetch_api("traffic/popular/paths")
    repo_info = fetch_api("")  # General repo details

    # 2. Load existing log
    history = load_history()

    # 3. Merge time-series data (Views & Clones)
    history["views"] = merge_time_series(history.get("views", {}), views_resp.get("views", []))
    history["clones"] = merge_time_series(history.get("clones", {}), clones_resp.get("clones", []))

    # 4. Save latest Top Referrers list
    history["top_referrers"] = [
        {
            "referrer": item.get("referrer"),
            "count": item.get("count"),
            "uniques": item.get("uniques")
        }
        for item in referrers_resp
    ]

    # 5. Save latest Popular Paths/Files list
    history["popular_paths"] = [
        {
            "path": item.get("path"),
            "title": item.get("title"),
            "count": item.get("count"),
            "uniques": item.get("uniques")
        }
        for item in paths_resp
    ]

    # 6. Store Repository Overview Stats
    history["repository_stats"] = {
        "stargazers_count": repo_info.get("stargazers_count", 0),
        "forks_count": repo_info.get("forks_count", 0),
        "subscribers_count": repo_info.get("subscribers_count", 0),  # Watchers
        "open_issues_count": repo_info.get("open_issues_count", 0),
        "size_kb": repo_info.get("size", 0)
    }

    # 7. Record Timestamp
    history["last_updated"] = datetime.utcnow().isoformat() + "Z"

    # Save to disk
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    print(f"All activity metrics updated successfully in '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()