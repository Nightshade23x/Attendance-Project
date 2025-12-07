from flask import Flask, render_template
import csv
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

def csv_exists(filename):
    try:
        with open(filename, "r"):
            return True
    except:
        return False

def load_attendance(filename="attendance.csv"):
    if not csv_exists(filename):
        return []
    records = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records

def calculate_stats(records):
    total_per_person = defaultdict(int)
    monthly_entries = defaultdict(int)
    today_entries = []

    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")

    for record in records:
        name = record["Name"]
        date = record["Date"]

        total_per_person[name] += 1

        if date.startswith(current_month):
            monthly_entries[name] += 1

        if date == today:
            today_entries.append(record)

    return total_per_person, monthly_entries, today_entries

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/stats")
def stats():
    records = load_attendance()
    total_per_person, monthly_entries, today_entries = calculate_stats(records)

    return render_template(
        "stats.html",
        total=total_per_person,
        monthly=monthly_entries,
        today=today_entries
    )

if __name__ == "__main__":
    app.run(debug=True)
