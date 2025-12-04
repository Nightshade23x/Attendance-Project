import csv
from datetime import datetime
from collections import defaultdict

def load_attendance(filename="attendance.csv"):
    if not csv_exists(filename):
        print("attendance csv not found")
        return []   

    records = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records

def csv_exists(filename):
    try:
        with open(filename, "r"):
            return True
    except:
        return False

def show_stats():
    records = load_attendance()
    if not records:
        return

    total_per_person = defaultdict(int)
    today_entries = []
    monthly_entries = defaultdict(int)

    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")

    for record in records:
        name = record["Name"]     
        date = record["Date"]     
        time = record["Time"]    

        total_per_person[name] += 1

        if date == today:
            today_entries.append(time)

        if date.startswith(current_month):
            monthly_entries[name] += 1

    print(" ATTENDANCE STATS")

    # Total per person
    print(" Total Logs Per Person:")
    for name, count in total_per_person.items():
        print(f"   - {name}: {count}")

    # Today stats
    print("\n Today Stats:")
    if today_entries:
        print(f"   - First Login: {min(today_entries)}")
        print(f"   - Last Login : {max(today_entries)}")
        print(f"   - Total Today: {len(today_entries)}")
    else:
        print("   - No entries today.")

    # Monthly stats
    print("\n Monthly Summary:")
    for name, count in monthly_entries.items():
        print(f"   - {name}: {count} this month")

if __name__ == "__main__":
    show_stats()
