from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import csv
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Email Setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mcoresidence@gmail.com'
app.config['MAIL_PASSWORD'] = 'lftiiuewhdhfurvs'  # Replace this with your actual app password
app.config['MAIL_DEFAULT_SENDER'] = 'mcoresidence@gmail.com'

mail = Mail(app)

# Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# WhatsApp Link
WHATSAPP_LINK = "https://wa.me/qr/4ZPX7LNRALZJG1"

# ✅ Homepage
@app.route("/")
def homepage():
    return render_template("index.html")  # Your homepage

# ✅ Booking form
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        date = request.form["date"]
        time = request.form["time"]
        payment_method = request.form["payment_method"]
        pickup = request.form["pickup"]
        pickup_location = request.form.get("pickup_location")
        early_checkin = request.form["early_checkin"]
        special_note = request.form.get("special_note")
        ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate the rate
        booking_duration = 0  # Default in case of invalid input
        rate = 0
        
        if request.form.get("duration") == "full_day":
            booking_duration = 1  # Full day or night
            rate = 450
        elif request.form.get("duration") == "2_hours":
            booking_duration = 2  # 2 hours
            rate = 250
        elif request.form.get("duration") == "extra_hour":
            booking_duration = 1  # Extra hour
            rate = 150

        total_amount = rate  # Default total for now

        if early_checkin == "yes":
            total_amount += 100  # Add charge for early check-in (if applicable)

        # Handle payment method and file upload
        if payment_method == "manual":
            file = request.files.get("payment_proof")
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Save to CSV
                with open("bookings.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now(), name, email, date, time, filename, payment_method, rate, total_amount])

                # Email to client
                try:
                    msg_client = Message("Booking Confirmation", recipients=[email])
                    msg_client.body = f"""
Hi {name},

Thank you for your booking on {date} at {time}.
Your reference number is: {ref_number}

We received your proof of payment.

Total: R{total_amount}

Banking details for your manual payment:
Amangcikwa Holdings PTY Ltd.
Account Number: 10233031039
Bank: Standard Bank

If you need help, feel free to contact us via WhatsApp: {WHATSAPP_LINK}

Kind regards,  
MCO Residence
                    """
                    mail.send(msg_client)
                except Exception as e:
                    print("Error sending email to client:", e)

                # Email to admin
                try:
                    admin_email = 'mcoresidence@gmail.com'
                    msg_admin = Message("New Manual Booking Received", recipients=[admin_email])
                    msg_admin.body = f"""
New Booking Details:

Name: {name}
Email: {email}
Date: {date}
Time: {time}
Reference Number: {ref_number}
Payment Method: Manual
Total Amount: R{total_amount}

Proof of payment attached.
                    """
                    with open(file_path, "rb") as fp:
                        msg_admin.attach(filename, file.content_type, fp.read())
                    mail.send(msg_admin)
                except Exception as e:
                    print("Error sending email to admin:", e)

            return render_template("success.html")

        elif payment_method == "online":
            # Save basic info to CSV
            with open("bookings.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now(), name, email, date, time, "N/A", payment_method, rate, total_amount])

            # Redirect to payment gateway (replace with actual payment gateway URL)
            payfast_url = f"https://www.payfast.co.za/eng/process?merchant_id=14070761&merchant_key=t9gho8csdpkwd&amount={total_amount}&item_name=MCO_Booking&email_address={email}&return_url=http://localhost:5000/success"
            return redirect(payfast_url)

    return render_template("booking.html")

# ✅ Success page
@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
