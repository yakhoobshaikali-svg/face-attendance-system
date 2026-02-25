from flask import Flask, render_template, request, redirect
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database
conn = sqlite3.connect("attendance.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS students (name TEXT, roll TEXT, image TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS attendance (name TEXT, roll TEXT, date TEXT, time TEXT)")
conn.commit()
conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        image = request.files["image"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(filepath)

        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("INSERT INTO students VALUES (?, ?, ?)", (name, roll, filepath))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/mark", methods=["POST"])
def mark():
    roll = request.form["roll"]

    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT name FROM students WHERE roll=?", (roll,))
    student = c.fetchone()

    if student:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)",
                  (student[0], roll, date, time))
        conn.commit()

    conn.close()
    return redirect("/attendance")

@app.route("/attendance")
def attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    records = c.fetchall()
    conn.close()
    return render_template("attendance.html", records=records)

if __name__ == "__main__":
    app.run()
