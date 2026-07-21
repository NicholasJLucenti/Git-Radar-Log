import os
import json
import requests
from datetime import datetime

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Replace these with the owner and name of the target repository you want to track
TARGET_REPO_OWNER = "NicholasJLucenti"
TARGET_REPO_NAME = "Git-Radar-Log"
OUTPUT_FILE = "traffic_history.json"

if not GITHUB_TOKEN:
    raise ValueError("Missing GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def fetch_traffic(endpoint):
    url = f"https://api.github.com/repos/{TARGET_REPO_OWNER}/{TARGET_REPO_NAME}/traffic/{endpoint}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def load_history():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {"views": {}, "clones": {}}

def merge_data(existing, new_entries):
    for entry in new_entries:
        date_str = entry["timestamp"].split("T")[0]
        existing[date_str] = {
            "count": entry["count"],
            "uniques": entry["uniques"]
        }
    return existing

def main():
    print(f"Fetching traffic for {TARGET_REPO_OWNER}/{TARGET_REPO_NAME}...")
    views_data = fetch_traffic("views").get("views", [])
    clones_data = fetch_traffic("clones").get("clones", [])

    history = load_history()
    history["views"] = merge_data(history.get("views", {}), views_data)
    history["clones"] = merge_data(history.get("clones", {}), clones_data)
    history["last_updated"] = datetime.utcnow().isoformat() + "Z"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
        
    print("Traffic updated successfully.")

if __name__ == "__main__":
    main()
