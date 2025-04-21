from flask import Flask, render_template, request
from flask_mail import Mail, Message
import csv
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mcoresidencel@gmail.com'       # Your sending Gmail
app.config['MAIL_PASSWORD'] = 'qkctdjrpbsgjnbtsf'              # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidencel@gmail.com' # Sender email

mail = Mail(app)

# Setup file upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route for index (home page)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        date = request.form["date"]
        time = request.form["time"]
        file = request.files["payment_proof"]

        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save booking info to CSV
        with open("bookings.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, email, date, time, filename])

        # Generate a reference number
        ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Send email to client
        msg = Message("Booking Confirmation", recipients=[email])
        msg.body = f"""
Hi {name},

Thank you for your booking on {date} at {time}.
Your reference number is: {ref_number}

We’ve received your proof of payment and will contact you soon to confirm your booking.

Warm regards,  
MC Residence
"""
        mail.send(msg)

        # Send email to admin (you)
        admin_email = 'mcoresidence@gmail.com'
        msg_admin = Message("New Booking Received", recipients=[admin_email])
        msg_admin.body = f"""
📩 New Booking Details:

Name: {name}
Email: {email}
Date: {date}
Time: {time}
Reference Number: {ref_number}
Proof of Payment Filename: {filename}

🗂 Check the uploaded file in: static/uploads/{filename}
"""
        mail.send(msg_admin)

        return render_template("success.html")

    return render_template("index.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
