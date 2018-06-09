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

# Bot's alert messages

first_message = "*Hey! This is a job alert!*"

no_vacancies_message = "*There're no new vacancies for the last day.*"

single_vacancy_warning_message = ("*There's a new vacancy for the last day!\n"
                                    "I'm sending it to you now...*")

plural_vacancy_warning_message = ("*There're {} new vacancies for the last day!\n"
                                    "I'm sending them to you now...*")

vacancy_message = ("*Vacancy #{count}* \n\n"
                    "*Title:* {title} \n"
                    "*Company:* {company} \n"
                    "*Location:* {location} \n"
                    "*Salary:* {salary} \n"
                    "*Short description:* \n{overview} \n\n"
                    "{url} ")


def send_alert():
    db = UserModel(dbname='../../db.sqlite3')
    user_list = db.get_items()
    # Get vacancies for the last day
    data = get_new_vacancies()
    # Compare old and new data. Get filtered new data.
    new_data = compare_data(data)
    if new_data:
        # Saving last sent vacancies
        with open('last_sent_vacancies.json', 'w+') as outfile:
            json.dump(new_data, outfile, indent=4, ensure_ascii=False)
    # Sending vacancies
    for user in user_list:
        send_message(chat_id=user, text=first_message)
        count = len(new_data)
        if count == 0:
            send_message(chat_id=user,
                         text=no_vacancies_message
                         )
        else:
            if count == 1:
                send_message(chat_id=user,
                             text=single_vacancy_warning_message.format(count)
                             )
            else:
                send_message(chat_id=user,
                             text=plural_vacancy_warning_message.format(count)
                             )
            for vacancy in new_data:
                send_message(chat_id=user,
                             text=vacancy_message.format(
                                                    count=count,
                                                    title=vacancy['title'],
                                                    company=vacancy['company'],
                                                    location=vacancy['location'],
                                                    salary=vacancy['salary'],
                                                    overview=vacancy['overview'],
                                                    url=vacancy['url']
                                                    )
                             )
                count -= 1
                time.sleep(.1)  # Wait 0.1 sec before the next vacancy


# Method for comparing new data to last sent
def compare_data(new_data):
    try:
        with open('last_sent_vacancies.json', 'r+') as f:
            if not os.stat("last_sent_vacancies.json").st_size:
                return new_data
            else:
                old_data = json.load(f)  # Get last sent vacancies
                for old_vacancy in old_data:
                    # TODO: Implement binary search algorithm here
                    if old_vacancy in new_data:
                        # Delete vacancy from data if the vacancy exists in last sent vacancies
                        new_data.pop(new_data.index(old_vacancy))
                    else:
                        continue
    except FileNotFoundError:
        return new_data
    return new_data


if __name__ == '__main__':
    send_alert()
