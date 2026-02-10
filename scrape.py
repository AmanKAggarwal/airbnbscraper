#!/usr/bin/env python3
"""
Airbnb listing availability scraper.
Runs daily via scheduled task, creates a new CSV per day.
Reads config from config.json.
"""

import pyairbnb
import csv
import json
import os
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def scrape():
    config = load_config()
    listing_ids = config["listing_ids"]
    months_ahead = config["months_ahead"]

    os.makedirs(DATA_DIR, exist_ok=True)

    scrape_date = date.today().isoformat()
    now = datetime.now()

    wanted = set()
    for i in range(months_ahead):
        m = now.month + i
        y = now.year
        if m > 12:
            m -= 12
            y += 1
        wanted.add((y, m))

    api_key = pyairbnb.get_api_key(proxy_url="")

    rows = []
    for listing_id in listing_ids:
        print(f"[{scrape_date}] Fetching calendar for listing {listing_id}...")
        calendar = pyairbnb.get_calendar(api_key=api_key, room_id=listing_id, proxy_url="")
        for month_data in calendar:
            if (month_data["year"], month_data["month"]) not in wanted:
                continue
            for day in month_data["days"]:
                rows.append([listing_id, day["calendarDate"], day["available"]])

    csv_file = os.path.join(DATA_DIR, f"airbnb_{scrape_date}.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["room_id", "date", "available"])
        writer.writerows(rows)

    print(f"[{scrape_date}] Wrote {len(rows)} rows to {csv_file}")


if __name__ == "__main__":
    scrape()
