"""
Bitcoin Analyzer Runner with Email
Runs the Bitcoin analysis and emails the HTML report
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from bitcoin_analyzer import run_bitcoin_analysis

# Fix Windows console encoding issues (only if not already wrapped)
if sys.platform == 'win32':
    try:
        import io
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            if not isinstance(sys.stdout, io.TextIOWrapper):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
            if not isinstance(sys.stderr, io.TextIOWrapper):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass  # Ignore if already wrapped, closed, or can't be wrapped

# Load environment variables
load_dotenv()

def send_email_with_html(html_file_path, recipient_email):
    """Send the HTML report via Gmail"""
    
    # Get Gmail credentials from .env
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    
    if not gmail_address or not gmail_password:
        raise ValueError("GMAIL_ADDRESS and GMAIL_PASSWORD must be set in .env file")
    
    if not os.path.exists(html_file_path):
        raise FileNotFoundError(f"HTML file not found: {html_file_path}")
    
    # Read the HTML content (try multiple encodings)
    html_content = None
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open(html_file_path, 'r', encoding=encoding, errors='replace') as f:
                html_content = f.read()
            break
        except Exception as e:
            continue
    
    if html_content is None:
        raise ValueError(f"Could not read HTML file with any encoding: {html_file_path}")
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = gmail_address
    msg['To'] = recipient_email
    msg['Subject'] = "Bitcoin Trading Analysis Report - Daily Update"
    
    # Create HTML email body
    html_body = f"""
    <html>
      <head></head>
      <body>
        <h2>Your Bitcoin Trading Analysis Report</h2>
        <p>Hey! Here's your daily Bitcoin analysis report. Check it out below!</p>
        <hr>
        {html_content}
      </body>
    </html>
    """
    
    # Attach HTML as both inline content and attachment
    part1 = MIMEText(html_body, 'html')
    msg.attach(part1)
    
    # Also attach the HTML file
    with open(html_file_path, 'rb') as f:
        part2 = MIMEBase('application', 'octet-stream')
        part2.set_payload(f.read())
        encoders.encode_base64(part2)
        part2.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(html_file_path)}'
        )
        msg.attach(part2)
    
    # Send email via Gmail SMTP
    try:
        print(f"Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print(f"Logging in as {gmail_address}...")
        server.login(gmail_address, gmail_password)
        
        print(f"Sending email to {recipient_email}...")
        text = msg.as_string()
        server.sendmail(gmail_address, recipient_email, text)
        server.quit()
        
        print(f"Email sent successfully to {recipient_email}!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def main():
    """Main function to run analysis and send email"""
    recipient_email = "tauhid.zaman@yale.edu"
    html_file = "output.html"
    
    print("="*80)
    print("BITCOIN ANALYSIS & EMAIL SENDER")
    print("="*80)
    print()
    
    # Step 1: Run the Bitcoin analysis
    print("Step 1: Running Bitcoin analysis...")
    print("-" * 80)
    try:
        run_bitcoin_analysis()
        print()
    except Exception as e:
        print(f"Error running analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    # Step 2: Check if HTML file was created
    if not os.path.exists(html_file):
        print(f"Error: {html_file} was not created. Cannot send email.")
        raise FileNotFoundError(f"{html_file} was not created")
    
    print()
    print("Step 2: Sending email...")
    print("-" * 80)
    
    # Step 3: Send the email
    success = send_email_with_html(html_file, recipient_email)
    
    if success:
        print()
        print("="*80)
        print("SUCCESS! Analysis complete and email sent!")
        print("="*80)
    else:
        print()
        print("="*80)
        print("Analysis complete but email failed to send.")
        print("="*80)
        raise Exception("Email failed to send")


if __name__ == "__main__":
    main()

