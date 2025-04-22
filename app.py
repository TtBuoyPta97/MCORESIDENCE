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
app.config['MAIL_USERNAME'] = 'mcoresidence@gmail.com'
app.config['MAIL_PASSWORD'] = 'lftiiuewhdhfurvs'
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidence@gmail.com'

mail = Mail(app)

# Upload folder for payment proof
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin email to receive attachments
admin_email = 'mcoresidence@gmail.com'  # Or change to a different admin email

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        date = request.form["date"]
        time = request.form["time"]
        file = request.files["payment_proof"]

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save to CSV
        with open("bookings.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, email, date, time, filename])

        # Generate reference number
        ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Send email to client
        try:
            msg_client = Message("Booking Confirmation", recipients=[email])
            msg_client.body = f"""
Hi {name},

Thank you for your booking on {date} at {time}.
Your reference number is: {ref_number}

We received your proof of payment.

Kind regards,
MCO Residence
            """
            mail.send(msg_client)
        except Exception as e:
            print("Error sending email to client:", e)

        # Send email to admin with attachment
        try:
            msg_admin = Message("New Booking Received", recipients=[admin_email])
            msg_admin.body = f"""
New Booking Details:

Name: {name}
Email: {email}
Date: {date}
Time: {time}
Reference Number: {ref_number}

Please see the attached proof of payment and confirm the booking.

Best,
MCO Residence
            """
            with open(file_path, "rb") as fp:
                msg_admin.attach(filename, file.content_type, fp.read())
            mail.send(msg_admin)
        except Exception as e:
            print("Error sending email to admin:", e)

        return render_template("success.html")

    return render_template("booking.html")

if __name__ == "__main__":
    app.run(debug=True)
