from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mcoresidence@gmail.com'
app.config['MAIL_PASSWORD'] = 'lftiiuewhdhfurvs'
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidence@gmail.com'
mail = Mail(app)

# Upload folder setup
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

WHATSAPP_LINK = "https://wa.me/qr/4ZPX7LNRALZJG1"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/booking", methods=["POST", "GET"])
def booking():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            cell = request.form["cell"]
            booking_type = request.form["booking_type"]
            checkin_date = request.form["checkin_date"]
            checkin_time = request.form["checkin_time"]
            payment_method = request.form["payment_method"]
            pickup = request.form["pickup"]
            pickup_location = request.form.get("pickup_location", "")
            special_note = request.form.get("special_note", "")

            checkin_datetime = datetime.strptime(f"{checkin_date}T{checkin_time}", "%Y-%m-%dT%H:%M")

            if booking_type == "1_hour":
                duration = 1
                rate = 150
                checkout_datetime = checkin_datetime + timedelta(hours=1)
            elif booking_type == "2_hour":
                duration = 2
                rate = 250
                checkout_datetime = checkin_datetime + timedelta(hours=2)
            elif booking_type == "night":
                checkout_date = request.form["checkout_date"]
                checkout_datetime = datetime.strptime(f"{checkout_date} 11:00", "%Y-%m-%d %H:%M")
                nights = (checkout_datetime.date() - checkin_datetime.date()).days
                nights = max(1, nights)
                duration = nights
                rate = 450
            else:
                return "Invalid booking type", 400

            total_cost = rate * duration

            filename = "N/A"
            filepath = None
            if payment_method == "manual":
                file = request.files.get("payment_proof")
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)

            ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Save to CSV
            with open("bookings.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(), name, email, cell, booking_type,
                    checkin_datetime, checkout_datetime, payment_method,
                    total_cost, filename, pickup, pickup_location, special_note, ref_number
                ])

            # Email to client
            msg_client = Message("MCO Booking Confirmation", recipients=[email])
            msg_client.body = f"""
Hi {name},

Thank you for your booking. Here are your details:

Reference: {ref_number}
Check-in: {checkin_datetime.strftime('%Y-%m-%d %H:%M')}
Check-out: {checkout_datetime.strftime('%Y-%m-%d %H:%M')}
Total: R{total_cost}
Pickup: {pickup} - {pickup_location}
Special Note: {special_note}

Payment Method: {payment_method.title()}

For Manual Payment:
Bank: Standard Bank
Name: Amangcikwa Holdings PTY Ltd
Acc No: 10233031039

Contact us on WhatsApp: {WHATSAPP_LINK}

Regards,
MCO Residence
            """
            mail.send(msg_client)

            # Email to you (admin)
            msg_admin = Message(f"New Booking Received - {ref_number}", recipients=["mcoresidence@gmail.com"])
            msg_admin.body = f"""
NEW BOOKING RECEIVED

Name: {name}
Email: {email}
Cell: {cell}
Reference: {ref_number}
Booking Type: {booking_type}
Check-in: {checkin_datetime.strftime('%Y-%m-%d %H:%M')}
Check-out: {checkout_datetime.strftime('%Y-%m-%d %H:%M')}
Total Cost: R{total_cost}
Payment Method: {payment_method}
Pickup: {pickup} - {pickup_location}
Special Note: {special_note}
            """
            if filepath:
                with app.open_resource(filepath) as fp:
                    msg_admin.attach(filename, "application/octet-stream", fp.read())

            mail.send(msg_admin)

            return render_template("summary.html",
                name=name,
                ref_number=ref_number,
                checkin=checkin_datetime.strftime("%Y-%m-%d %H:%M"),
                checkout=checkout_datetime.strftime("%Y-%m-%d %H:%M"),
                total_cost=total_cost,
                payment_method=payment_method,
                whatsapp_link=WHATSAPP_LINK,
                show_payment_link=(payment_method == "online"),
                payfast_url=f"https://www.payfast.co.za/eng/process?merchant_id=14070761&merchant_key=t9gho8csdpkwd&amount={total_cost}&item_name=MCO_Booking&email_address={email}"
            )
        except Exception as e:
            print("Booking error:", e)
            return "Something went wrong. Please check your input or try again later.", 400

    return render_template("booking.html")

@app.route("/success")
def success():
    return render_template("success.html")
