# -*- coding: utf-8 -*-

from datetime import datetime
from google_tools.google_api import pull_gsheet_data
import time

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def pull_sot_calendar_df(): ##move to general tools
    # pull the sot calendar
    sheet_id = '1h9IjgBXuGfTYInkV0qFl_R5-X7EwfbWsuUYj3nBjMgg'
    range_name = 'calendar!A:Z'
    print("loading SOT calender")
    sot_calendar_df = pull_gsheet_data(sheet_id, range_name)
    print("SOT calendar loaded")
    return sot_calendar_df
