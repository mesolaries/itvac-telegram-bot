"""
This module is for generating and sending alerts to users.

send_alert() method gets all users from database who set alerts.
Next, it calls get_new_vacancies() method and gets new data.
Then, it calls compare_data() method to compare new and last sent data. And returns new filtered data.
If filtered data is not empty, the alert will be sent to the users.
The filtered data will be written to last_sent_vacancies.json file.

last_sent_vacancies.json file will be created after first run send_alert.py module

"""

from vacancies import get_new_vacancies
from message import send_message
from alert_db_access import UserModel
import json
import os
import time


def send_alert():
    db = UserModel(dbname='../../db.sqlite3')
    user_list = db.get_items()
    # Get vacancies for the last day
    data = get_new_vacancies()
    # Compare old and new data. Get filtered new data.
    new_data = compare_data(data)
    if new_data:
        # Saving all sent vacancies
        with open('last_sent_vacancies.json', 'w') as outfile:
            json.dump(new_data, outfile, indent=4, ensure_ascii=False)
    # Sending vacancies
    for user in user_list:
        send_message(chat_id=user,
                     text="*Hey! This is a job alert!*"
                     )
        count = len(new_data)
        if count == 0:
            send_message(chat_id=user,
                         text="*There're no new vacancies for the last 12 hours.*"
                         )
        else:
            if count == 1:
                send_message(chat_id=user,
                             text="*There's 1 new vacancy for the last 12 hours!\n"
                                  "I'm sending it to you now...*".format(count)
                             )
            else:
                send_message(chat_id=user,
                             text="*There're {} new vacancies for the last 12 hours!\n"
                                  "I'm sending them to you now...*".format(count)
                             )
            time.sleep(3)  # Wait 3 secs, then send vacancies
            for vacancy in new_data:
                send_message(chat_id=user,
                             text="*Vacancy #" + str(count) + '*\n\n'
                                    "*Job title: *" + vacancy['title'] + '\n'
                                    "*Location: *" + vacancy['location'] + '\n'
                                    "*Salary: *" + vacancy['salary'] + '\n'
                                    "*Company: *" + vacancy['company'] + '\n'
                                    "*Overview: *" + vacancy['overview'] + '\n\n'
                                    "" + vacancy['url'] + ' '
                             )
                count -= 1
                time.sleep(1) # Wait a sec before the next vacancy


# Method for comparing new data to last sent
def compare_data(new_data):
    with open('last_sent_vacancies.json', 'w') as f:  # Opening file in w mode prevents error when file doesn't exist
        if not os.stat("last_sent_vacancies.json").st_size:
            return new_data
        else:
            old_data = json.load(f)  # Get last sent vacancies
            for old_vacancy in old_data:
                if old_vacancy in new_data:
                    # Delete vacancy from data if the vacancy exists in last sent vacancies
                    new_data.pop(new_data.index(old_vacancy))
                else:
                    continue
    return new_data


if __name__ == '__main__':
    send_alert()