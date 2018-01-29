from vacancies import get_new_vacancies
from message import send_message
from reminder.db_reminder import UserModel
import json
import os
import time


def send_reminder():
    db = UserModel(dbname='../../db.sqlite3')
    user_list = db.get_items()
    # Get vacancies for the last day
    data = get_new_vacancies()
    new_data = compare_data(data)
    for user in user_list:
        count = len(new_data)
        send_message(chat_id=user,
                     text="*Hey! This is a reminder!*"
                     )
        if count == 0:
            send_message(chat_id=user,
                         text="*There're no new vacancies for the last 12 hours.*"
                         )
        else:
            send_message(chat_id=user,
                         text="*There're {} new vacancies for the last 12 hours!\n"
                              "I'm sending them to you now...*".format(count)
                         )
            time.sleep(3)
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
    # Saving all sent vacancies
    with open('last_sent_reminder.json', 'w') as outfile:
        json.dump(new_data, outfile, indent=4, ensure_ascii=False)


def compare_data(new_data):
    with open('last_sent_reminder.json', 'r+') as f:
        if not os.stat("last_sent_reminder.json").st_size:
            return new_data
        else:
            old_data = json.load(f)
            for old_vacancy in old_data:
                if old_vacancy in new_data:
                    new_data.pop(new_data.index(old_vacancy))
                else:
                    continue
    return new_data


if __name__ == '__main__':
    send_reminder()