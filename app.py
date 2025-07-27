# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing your frontend to connect

# Email configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') # App-specific password for Gmail
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'zuratavartkiladze882@gmail.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587)) # 587 for TLS, 465 for SSL

@app.route('/send-email', methods=['POST'])
def send_email():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json()
    form_type = data.get('formType') # e.g., 'contactUs', 'aboutUsContact', 'becomeMember'
    name = data.get('name')
    surname = data.get('surname') # New field
    email = data.get('email')
    phone = data.get('phone') # New field
    message = data.get('message')
    kvkk = data.get('kvkk') # New field (boolean)
    subject = data.get('subject', 'New Form Submission') # Default subject

    # Basic validation - adjust as per your required fields
    if not all([form_type, name, surname, email, message, kvkk is not None]):
        return jsonify({"message": "Missing required fields (formType, name, surname, email, message, kvkk)"}), 400
    
    # Ensure KVKK is true
    if not kvkk:
        return jsonify({"message": "KVKK approval is required"}), 400

    # Customize subject based on form type
    if form_type == 'contactUs':
        subject = f"New Contact Us Message from {name} {surname}"
    elif form_type == 'aboutUsContact': # Assuming a contact form in about us
        subject = f"New About Us Contact Message from {name} {surname}"
    elif form_type == 'becomeMember': # Assuming a 'become a member' form
        subject = f"New Member Application from {name} {surname}"
    else:
        subject = f"New General Form Submission from {name} {surname}"


    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject

        # Enhanced body for all fields
        body = f"""
        <html>
        <body>
            <h3>Form Submission Details:</h3>
            <p><strong>Form Type:</strong> {form_type}</p>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Surname:</strong> {surname}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone if phone else 'N/A'}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
            <p><strong>KVKK Approved:</strong> {'Yes' if kvkk else 'No'}</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully for {form_type} form from {name} {surname}.") # For server logs
        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        print(f"Error sending email: {e}") # For server logs
        return jsonify({"message": f"Failed to send email: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Run on port 5000 for local testing