from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import csv
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Email Setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mcoresidence@gmail.com'
app.config['MAIL_PASSWORD'] = 'lftiiuewhdhfurvs'  # Replace with your actual app password
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
        checkin_date = request.form["checkin_date"]
        checkout_date = request.form["checkout_date"]
        checkin_time = request.form["checkin_time"]
        checkout_time = request.form["checkout_time"]
        payment_method = request.form["payment_method"]
        pickup = request.form["pickup"]
        pickup_location = request.form.get("pickup_location")
        early_checkin = request.form["early_checkin"]
        special_note = request.form.get("special_note")
        ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Combine date and time to get the full datetime
        checkin_datetime = datetime.strptime(f"{checkin_date} {checkin_time}", "%Y-%m-%d %H:%M")
        checkout_datetime = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y-%m-%d %H:%M")

        # Calculate the duration of the stay in hours
        duration = (checkout_datetime - checkin_datetime).total_seconds() / 3600  # Duration in hours

        if duration <= 2:
            rate = 250  # For 2 hours
        elif duration <= 24:
            rate = 450  # For a full day or night (up to 24 hours)
        else:
            rate = 150  # For extra hours after 24 hours

        total_amount = rate * duration

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
                    writer.writerow([datetime.now(), name, email, checkin_datetime, checkout_datetime, filename, payment_method, rate, total_amount])

                # Email to client
                try:
                    msg_client = Message("Booking Confirmation", recipients=[email])
                    msg_client.body = f"""
Hi {name},

Thank you for your booking from {checkin_datetime} to {checkout_datetime}.
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
Check-in Date and Time: {checkin_datetime}
Check-out Date and Time: {checkout_datetime}
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
                writer.writerow([datetime.now(), name, email, checkin_datetime, checkout_datetime, "N/A", payment_method, rate, total_amount])

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
