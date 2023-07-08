# %%
import os
from dotenv import load_dotenv, find_dotenv
from utils import mail_sender, email_content_template

from datetime import date

_ = load_dotenv(find_dotenv())


# %%
th_styles = """align='left' bgcolor='#0072e8' style='color: white; padding: 15px; border: 1px solid black;'"""
td_styles = """align='right' style='padding: 15px; border: 1px solid black;'"""
table_styles = """style='border: 1px solid black;'"""
main_table = f"""
<table class="dataframe" {table_styles}>
  <tbody>
    <tr>
      <th {th_styles}>name</th>
      <td {td_styles}>your name</td>
    </tr>
    <tr>
      <th {th_styles}>date</th>
      <td {td_styles}>2023-07-08</td>
    </tr>
    <tr>
      <th {th_styles}>who did you talk to this week?</th>
      <td {td_styles}>best friend</td>
    </tr>
    <tr>
      <th {th_styles}>who is your best friend?</th>
      <td {td_styles}>Jms</td>
    </tr>
  </tbody>
</table>"""

# %%
email_content = email_content_template(
    email_body=main_table,
)
receiver_email = os.getenv("GMAIL_RECEIVER_EMAIL")
mail_sender(
    to_address=receiver_email,
    subject="An email from mail-srvyr",
    html_body=email_content,
)

# %%
