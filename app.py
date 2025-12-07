from flask import Flask, render_template, request, Response,redirect, url_for,session
import csv
from datetime import datetime
from collections import defaultdict
import cv2
from deepface import DeepFace
import os

app = Flask(__name__)
app.secret_key="sammyxxx"


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


def mark_attendance(name):
    if not os.path.exists("attendance.csv"):
        with open("attendance.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time"])

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    with open("attendance.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, date_str, time_str])

    print(f"[LOGGED] {name} at {date_str} {time_str}")


last_logged = {}   # global for the flask webcam session




def gen_frames():
    cam = cv2.VideoCapture(0)

    while True:
        success, frame = cam.read()
        if not success:
            break

        
        try:
            result = DeepFace.verify(
                img1_path=frame,
                img2_path="known/Samar.jpg",
                enforce_detection=False
            )

            if result["verified"]:
                name = "Samar"
            else:
                name = "Unknown"

        except:
            name = "Unknown"

        
        now_minute = datetime.now().strftime("%H:%M")

        if name == "Samar":
            if "Samar" not in last_logged or last_logged["Samar"] != now_minute:
                mark_attendance("Samar")
                last_logged["Samar"] = now_minute

       
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.putText(frame, name, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)

    
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/stats")
def stats():
    if not session.get("logged_in"):
        return redirect("/login")

    records = load_attendance()

    selected_name = request.args.get("name", "")
    selected_date = request.args.get("date", "")

    filtered = []
    for r in records:
        if selected_name and r["Name"] != selected_name:
            continue
        if selected_date and r["Date"] != selected_date:
            continue
        filtered.append(r)

    total, monthly, today = calculate_stats(filtered)
    names = sorted(set(r["Name"] for r in records))

    return render_template(
        "stats.html",
        total=total,
        monthly=monthly,
        today=today,
        names=names,
        selected_name=selected_name,
        selected_date=selected_date
    )

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/live")
def live():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("live.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # CHANGE THESE TO YOUR OWN CREDENTIALS
        if username == "samar" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
