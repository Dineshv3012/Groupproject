from flask import Flask, request, jsonify
from datetime import datetime, time
from twilio.rest import Client
from dotenv import load_dotenv
import os
import json
import threading
import time as t

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_AUTH)
app = Flask(__name__)

with open("students.json") as f:
    students = json.load(f)

attendance = {}

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def send_message(to, message):
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=to
        )
        print(f"Sent to {to}: {message.sid}")
    except Exception as e:
        print(f"Error sending to {to}: {e}")

@app.route("/scan", methods=["GET"])
def scan():
    student_id = request.args.get("id")
    now = datetime.now()
    current_time = now.time()
    today = get_today()

    if student_id not in students:
        return jsonify({"error": "Invalid student ID"}), 400

    if today not in attendance:
        attendance[today] = {}

    if student_id in attendance[today]:
        return jsonify({"message": "Already scanned", "status": attendance[today][student_id]})

    if current_time < time(8, 25):
        status = "Present"
    elif current_time < time(8, 35):
        status = "Late"
        send_message(students[student_id]["parent_contact"], f"Your student {students[student_id]['name']} is late today.")
    else:
        return jsonify({"error": "Scan window closed"}), 403

    attendance[today][student_id] = status
    return jsonify({"student": students[student_id]["name"], "status": status})

@app.route("/attendance", methods=["GET"])
def get_attendance():
    today = get_today()
    return jsonify(attendance.get(today, {}))

def mark_absentees():
    today = get_today()
    if today not in attendance:
        attendance[today] = {}

    for sid in students:
        if sid not in attendance[today]:
            attendance[today][sid] = "Absent"
            send_message(students[sid]["parent_contact"], f"Your student {students[sid]['name']} is absent today.")
    print("Absentees marked.")

def schedule_absent_check():
    def check_loop():
        while True:
            now = datetime.now()
            if now.hour == 8 and now.minute == 35:
                mark_absentees()
                t.sleep(60)
            t.sleep(30)
    thread = threading.Thread(target=check_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    schedule_absent_check()
    app.run(host="0.0.0.0", port=5000)