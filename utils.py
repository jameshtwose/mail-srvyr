import os
import pandas as pd
import smtplib
import ssl
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from imapclient import IMAPClient
import email
from bs4 import BeautifulSoup


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


def request_email_info(email_amount: int = 50):
    """Request email data from IMAP server and return as a pandas DataFrame

    Parameters
    ----------
    email_amount : int
        Amount of emails to request from IMAP server. Default is 50. Used to minimize time spent requesting data.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing email data

    """
    server = IMAPClient(
        host=os.environ["IMAP_SERVER"], ssl=True, port=993, use_uid=True
    )
    server.login(
        username=os.environ["GMAIL_SENDER_EMAIL"],
        password=os.environ["GMAIL_SENDER_PASS_KEY"],
    )

    select_info = server.select_folder("INBOX")
    print("%d messages in INBOX" % select_info[b"EXISTS"])

    messages = server.search()

    info_df = pd.DataFrame()
    for msgid, data in server.fetch(messages[-email_amount:], ["ENVELOPE"]).items():
        envelope = data[b"ENVELOPE"]
        tmp_df = pd.DataFrame(
            {
                "msgID": msgid,
                "from": str(envelope.from_[0].name)[1:].replace("'", ""),
                "subject": envelope.subject.decode(),
                "date_received": envelope.date,
            },
            index=[0],
        )
        info_df = pd.concat([info_df, tmp_df])
    _ = info_df.reset_index(drop=True, inplace=True)

    # %%
    body_df = pd.DataFrame()
    for msgid, data in server.fetch(messages[-email_amount:], ["BODY[TEXT]"]).items():
        body = data[b"BODY[TEXT]"]
        body_obj = email.message_from_bytes(body)
        msg = body_obj.get_payload(decode=True)
        if msg:
            try:
                soup = BeautifulSoup(msg.decode(encoding="windows-1254"), "html.parser")
            except UnicodeDecodeError:
                soup = BeautifulSoup(msg.decode(encoding="utf-8"), "html.parser")

            table_content = soup.find("table")
            if table_content:
                current_df = (
                    pd.read_html(table_content.prettify())[0]
                    .set_index(0)
                    .T.reset_index(drop=True)
                    .pipe(lambda x: x.apply(lambda col: col.str.replace("= ", "")))
                )
                body_df = pd.concat([body_df, current_df])

    return select_info[b"EXISTS"], info_df, body_df
