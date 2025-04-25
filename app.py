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

# Upload setup
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# WhatsApp link
WHATSAPP_LINK = "https://wa.me/qr/4ZPX7LNRALZJG1"

@app.route("/")
def home():
    return render_template("index.html")  # Change this to the homepage template

@app.route("/booking", methods=["POST", "GET"])
def booking():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            booking_type = request.form["booking_type"]
            checkin_date = request.form["checkin_date"]
            checkin_time = request.form["checkin_time"]
            payment_method = request.form["payment_method"]
            pickup = request.form["pickup"]
            pickup_location = request.form.get("pickup_location", "")
            early_checkin = request.form.get("early_checkin", "no")
            special_note = request.form.get("special_note", "")

            checkin_datetime = datetime.strptime(f"{checkin_date} {checkin_time}", "%Y-%m-%dT%H:%M")

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
                rate = 450
                duration = nights
            else:
                return "Invalid booking type", 400

            total_cost = rate * duration

            if early_checkin == "yes":
                total_cost += 100

            filename = "N/A"
            if payment_method == "manual":
                file = request.files.get("payment_proof")
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            ref_number = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Save to CSV
            with open("bookings.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now(), name, email, booking_type, checkin_datetime,
                                 checkout_datetime, payment_method, total_cost, filename, ref_number])

            # Email
            msg = Message("MCO Booking Confirmation", recipients=[email])
            msg.body = f"""
            Hi {name},

            Thank you for your booking. Here are your details:

            Reference: {ref_number}
            Check-in: {checkin_datetime.strftime('%Y-%m-%d %H:%M')}
            Check-out: {checkout_datetime.strftime('%Y-%m-%d %H:%M')}
            Total: R{total_cost}

            Payment Method: {payment_method.title()}

            Banking details (for manual payment):
            Amangcikwa Holdings PTY Ltd.
            Account Number: 10233031039
            Bank: Standard Bank

            Contact us on WhatsApp: {WHATSAPP_LINK}

            Regards,
            MCO Residence
            """
            mail.send(msg)

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

    return render_template("booking.html")  # Renders the booking page when GET request is made

if __name__ == "__main__":
    app.run(debug=True)
