# %%
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from utils import request_email_info

_ = load_dotenv(find_dotenv())
# %%
select_info, info_df, body_df = request_email_info(email_amount=50)
# %%
select_info
# %%
info_df
# %%
body_df
# %%
