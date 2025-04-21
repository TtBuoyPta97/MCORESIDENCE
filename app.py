from flask import Flask, render_template, request
from flask_mail import Mail, Message
import csv
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
app.config['MAIL_PORT'] = 587                # Gmail SMTP port
app.config['MAIL_USE_TLS'] = True            # Use TLS for security
app.config['MAIL_USERNAME'] = 'mcoresidencel@gmail.com'   # Replace with your email
app.config['MAIL_PASSWORD'] = 'irfnfvdrlbckaguf'      # Replace with your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidence@gmail.com'  # Same email here

mail = Mail(app)

# Setup file upload folder
UPLOAD_FOLDER = 'static/uploads'
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

        # Save uploaded proof of payment
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save booking info to CSV
        with open("bookings.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, email, date, time, filename])

        # Create a reference number for the booking
        ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Send confirmation email to client
        msg = Message("Booking Confirmation", recipients=[email])
        msg.body = f"""
Hi {name},

Thank you for your booking on {date} at {time}.
Your reference number is: {ref_number}

We received your proof of payment.

Kind regards,
Your Business Name
        """
        mail.send(msg)

        # Send email to admin (you) with booking details
        admin_email = 'mcoresidence@gmail.com'  # Replace with your admin email

        msg_admin = Message("New Booking Received", recipients=[admin_email])
        msg_admin.body = f"""
New Booking Details:

Name: {name}
Email: {email}
Date: {date}
Time: {time}
Reference Number: {ref_number}
Proof of Payment: {file_path}

Please check the payment proof and confirm the booking.

Best,
Your Business Name
"""
        mail.send(msg_admin)

        return render_template("success.html")
    
    return render_template("index.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
