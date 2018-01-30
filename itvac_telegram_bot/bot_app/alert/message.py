"""
This module is for creating message templates.
"""

import requests
import os

# Get token from environment variable if this module called by send_alert.py
# Otherwise token is coming from wsgi
token = os.environ.get('TOKEN')  # Will not work on local. Need to set env variable on local machine
base_url = "https://api.telegram.org/bot{}/".format(token)


# Message template
def send_message(chat_id, text, parse_mode="Markdown", reply_to_message_id=''):
    url = base_url + 'sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'reply_to_message_id': reply_to_message_id
    }
    request = requests.post(url, json=answer)
    response = request.json()
    return response
