from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]

        with open("bookings.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, date, time])

        return "Booking received! Thank you."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
