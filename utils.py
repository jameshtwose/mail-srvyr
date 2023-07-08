import os
import smtplib
import ssl
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def mail_sender(
    to_address=os.getenv("GMAIL_RECEIVER_EMAIL"),
    subject="An email from BusinessAnalytiq SMRZR",
    html_body="""<html>
                <body>
                <h4>Hi,<br><br>
                Thank you very much for using SMRZR from 
                <a href="https://businessanalytiq.com">Business Analytiq</a>.<br><br>
                Cheers,<br>
                The Business Analytiq Team
                </h4>
                </body>
                </html>""",
):
    """
    Sends an email to a specified address.

    Parameters
    ----------
    to_address : str
        Email address to send email to.
    subject : str
        Subject of email.
    body : str
        Body of email.

    Returns
    -------
    None

    """

    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    password = os.getenv("GMAIL_SENDER_PASS_KEY")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_address

    # Create the plain-text and HTML version of your message
    text = "Please view this email in an HTML compatible email client."

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html_body, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # CSV attachment
    filename = "./ba_smrzr.csv"
    try:
        with open(filename, "rb") as fs:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(fs.read())
        if part:
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", "attachment", filename=os.path.basename(filename)
            )
            message.attach(part)
    except FileNotFoundError:
        print("No CSV file found to attach.")

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, to_address, message.as_string())
        print("mail_sender() completed successfully.")

        
def email_content_template(email_body: str):
    """
    Creates the email template.

    Parameters
    ----------
    email_body : str
        Body of the email.

    Returns
    -------
    str
        Email template.

    Examples
    --------
    >>> from utils import email_content_template
    >>> email_content_template("This is a test.")

    """
    return f"""
    <html>
    <body>
    <p>To whom it may concern,<br><br>
    Here is your latest reminder to fill in your weekly survey. 
    Please fill in the following table below and <strong>reply to this email address with the response:<strong/><br><br>
    </p>
    {email_body}
    <br><br>
    <p>Thank you very much for using mail-srvyr from
    <a href="https://services.jms.rocks">James Twose</a>.<br><br>
    Cheers,<br><br>
    James<br>
    <img src="https://services.jms.rocks/img/logo.png" alt="Jms Logo" height="80"><br>
    </p>
    </body>
    </html>
    """