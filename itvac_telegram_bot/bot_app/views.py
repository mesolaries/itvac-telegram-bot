# from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from datetime import datetime
from json.decoder import JSONDecodeError
import re
import json
import time
import traceback
import os

from bot_app.models import User, Alert
from bot_app.alert.vacancies import get_random_vacancy
from bot_app.alert.message import send_message

# Bot's text messages

start_message = ("Hi! I'm IT Vacancies Bot.\n"
                "I'll send you all new IT vacancies available on the web once a day.\n"
                "Send /vacancy to get a random vacancy from all available for the past week.")

no_vacancy_message = ("Sorry. No vacancies available for now...\n"
                        "Please, try again later.")

vacancy_message = ("*Title:* {title} \n"
                    "*Company:* {company} \n"
                    "*Location:* {location} \n"
                    "*Salary:* {salary} \n"
                    "*Short description:* \n{overview} \n\n"
                    "{url} ")

subscribed_message = ("You've subscribed to vacancy updates.\n"
                        "Now, you'll get all new vacancies available on the web once a day.")

already_subscribed_message = ("You've already subscribed to vacancy updates.\n"
                                "Send /unsetalert if you want to unsubscribe.")

unset_alert_message = ("You've unsubscribed from vacancy updates.\n"
                        "You'll no longer get alerts about new vacancies available.\n"
                        "Send /setalert if you want to get them again.")

help_message = ("*How to use IT Vacancies bot?\n\n*"
                "*This bot connects to popular vacancy websites and scrapes all new IT vacancies available.\n"
                "So, you don't have to manually check websites every time.\n\n*"
                "Here are the control commands of the bot:\n"
                "/start - Starts the bot and automatically subscribes you to the daily vacancy updates.\n"
                "/vacancy - Get a random vacancy from all available vacancies for the past week.\n"
                "/setalert - Subscribe to the daily vacancy updates. So, you'll get all new vacancies available every day.\n"
                "/unsetalert - Unsubscribe from daily vacancy updates. You'll no longer get vacancy notifications.\n"
                "/help - You'll get this help message.\n\n"
                "_Note: This bot only works with Azerbaijan vacancy websites._\n\n"
                "*Join the channel:* [@it_vakansiyalar](tg://user?id=@it_vakansiyalar)\n"
                "*GitHub repo:* https://github.com/mesolaries/itvac-telegram-bot")

# Add your handlers here
def start(chat_id, username):
    message = send_message(chat_id, text=start_message)
    try:
        # Create object if doesn't exist. Update username if changed.
        User.objects.update_or_create(chat_id=chat_id, defaults={'username': username})
    except IntegrityError:
        pass
    finally:
        try:
            Alert.objects.create(chat_id=chat_id)
        except IntegrityError:
            pass
    return message


def vacancy(chat_id, message_id):
    vac = get_random_vacancy()
    if len(vac) == 0:
        message = send_message(chat_id,
                                 reply_to_message_id=message_id,
                                 text=no_vacancy_message
                               )
    else:
        message = send_message(chat_id,
                                reply_to_message_id=message_id,
                                text=vacancy_message.format(
                                                            title=vac['title'],
                                                            company=vac['company'],
                                                            location=vac['location'],
                                                            salary=vac['salary'],
                                                            overview=vac['overview'],
                                                            url=vac['url']
                                                        )
                               )
    return message


def set_alert(chat_id, message_id, username):
    # Prevents referenced before assignment error if there'll be error other than IntegrityError
    message = {}
    try:
        Alert.objects.create(chat_id=chat_id)
        message = send_message(chat_id,
                                 reply_to_message_id=message_id,
                                 text=subscribed_message
                               )
    except IntegrityError:
        message = send_message(chat_id,
                                 reply_to_message_id=message_id,
                                 text=already_subscribed_message
                               )
    finally:
        try:
            User.objects.update_or_create(chat_id=chat_id, defaults={'username': username})
        except IntegrityError:
            pass
    return message


def help(chat_id, message_id):
    message = send_message(chat_id=chat_id,
                             reply_to_message_id=message_id,
                             text=help_message
                 )
    return message


def unset_alert(chat_id, message_id):
    try:
        Alert.objects.filter(chat_id=chat_id).delete()
        message = send_message(chat_id,
                                 reply_to_message_id=message_id,
                                 text=unset_alert_message
                               )
    except:
        message = {}
    return message


# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class CommandReceiveView(View):
    def get(self, request):
        return HttpResponse(status=200)

    def post(self, request):
        try:
            data = json.loads(request.read().decode('utf-8'))
            chat_id = data['message']['chat']['id']
            # Get username (private chat). If not available get group title (group chat).
            username = data['message']['chat'].get('username', data['message']['chat'].get('title'))
            message = data['message']['text']
            message_id = data['message']['message_id']
            pattern = r'/\w+'
            get_command = re.search(pattern, message)
            try:
                command = get_command.group()
            except:
                command = None

            if command == '/start':
                start(chat_id, username)
            elif command == '/vacancy':
                vacancy(chat_id, message_id)
            elif command == '/unsetalert':
                unset_alert(chat_id, message_id)
            elif command == '/setalert':
                set_alert(chat_id, message_id, username)
            elif command == '/help':
                help(chat_id, message_id)
        except:
            current_time = datetime.now().strftime("%I:%M%p on %B %d, %Y")
            tb = traceback.format_exc().replace('\n', ' ')
            error_data = {
                'time': current_time,
                'request': str(json.loads(request.read().decode('utf-8'))),
                'error': tb
            }
            path = os.path.dirname(os.path.realpath(__file__))
            try:
                with open(path + "/logs/caught_exceptions.log", 'r+') as log:
                    try:  # If file is not empty
                        current_log = json.load(log)
                        current_log.append(error_data)
                        with open(path + "/logs/caught_exceptions.log", 'w+') as f:
                            json.dump(current_log, f, indent=4, ensure_ascii=False)
                    except JSONDecodeError:  # If file is empty
                        json.dump([error_data], log, indent=4, ensure_ascii=False)
            except FileNotFoundError:
                with open(path + "/logs/caught_exceptions.log", 'w+') as log:
                    json.dump([error_data], log, indent=4, ensure_ascii=False)
        finally:
            time.sleep(1)  # Wait a sec before end this request and start a new one
            return HttpResponse(status=200)

# Main page views
# Redirects to bot chat

def main(request):
    return redirect("https://t.me/itvac_bot")
