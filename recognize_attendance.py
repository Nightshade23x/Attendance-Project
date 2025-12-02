import cv2
from deepface import DeepFace
import os
import csv
from datetime import datetime

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


def start_attendance():
    cap = cv2.VideoCapture(0)

    last_logged = {}     # avoid duplicate logs

    while True:
        ret, frame = cap.read()
        if not ret:
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

        # display name
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.putText(frame, name, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)

        # prevent logging every frame
        now_minute = datetime.now().strftime("%H:%M")
        if name == "Samar":
            if "Samar" not in last_logged or last_logged["Samar"] != now_minute:
                mark_attendance("Samar")
                last_logged["Samar"] = now_minute

        cv2.imshow("Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_attendance()
