# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication # Import for file attachments
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
    # Determine if it's a JSON request or a multipart/form-data request (for file upload)
    if request.is_json:
        data = request.get_json()
        form_type = data.get('formType')
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        kvkk = data.get('kvkk')
        subject = data.get('subject', 'New Form Submission')
        uploaded_file = None # No file in JSON request
    elif request.content_type and 'multipart/form-data' in request.content_type:
        # This is likely the "Become a Member" form with a file
        form_type = request.form.get('formType')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        kvkk = request.form.get('kvkk') # This will be a string 'true' or 'false'
        subject = request.form.get('subject', 'New Form Submission')
        uploaded_file = request.files.get('cvFile') # Get the uploaded file
    else:
        return jsonify({"message": "Unsupported Media Type"}), 415

    # Basic validation - adjust as per your required fields
    # Note: kvkk from FormData will be a string, convert to boolean
    is_kvkk_approved = str(kvkk).lower() == 'true'

    if not all([form_type, name, surname, email, message is not None, is_kvkk_approved]):
        # Removed explicit check for phone as it might be optional
        return jsonify({"message": "Missing required fields (formType, name, surname, email, message, KVKK approval)"}), 400
    
    # Ensure KVKK is true
    if not is_kvkk_approved:
        return jsonify({"message": "KVKK approval is required"}), 400

    # Customize subject based on form type
    if form_type == 'contactUs':
        subject = f"New Contact Us Message from {name} {surname}"
    elif form_type == 'aboutUsContact':
        subject = f"New About Us Contact Message from {name} {surname}"
    elif form_type == 'becomeMember':
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
            <p><strong>KVKK Approved:</strong> {'Yes' if is_kvkk_approved else 'No'}</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach file if present
        if uploaded_file:
            # Read the file content
            file_data = uploaded_file.read()
            # Get filename and mimetype
            filename = uploaded_file.filename
            # Use MIMEApplication for generic file attachments
            part = MIMEApplication(file_data, Name=filename)
            # Add header for Content-Disposition, important for attachment in email clients
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)
            print(f"Attached file: {filename}") # For server logs

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully for {form_type} form from {name} {surname}.")
        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"message": f"Failed to send email: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)