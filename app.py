from flask import Flask, render_template, request
from flask_mail import Mail, Message
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mcoresidence@gmail.com'       
app.config['MAIL_PASSWORD'] = 'irfn fvdr lbck aguf'          
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidence@gmail.com'

mail = Mail(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
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

        # Create a reference number
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

        return "Booking received! Confirmation email sent."

    return render_template("index.html")
    
