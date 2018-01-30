# from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import re
import json

from bot_app.models import User, Alert
from bot_app.alert.vacancies import get_random_vacancy
from bot_app.alert.message import send_message


# Add your handlers here
def start(chat_id, username):
    response = send_message(chat_id,
                            text="Hi! I'm IT Vacancies Bot.\n"
                                 "I'll send you updates about new IT vacancies available on the web twice a day."
                            )
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
    return response


def vacancy(chat_id, message_id):
    vac = get_random_vacancy()
    if len(vac) == 0:
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="Sorry. No vacancies available for now...\n"
                          "Please, try again later."
                     )
    else:
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="*Job title: *" + vac['title'] + '\n'
                            "*Location: *" + vac['location'] + '\n'
                            "*Salary: *" + vac['salary'] + '\n'
                            "*Company: *" + vac['company'] + '\n'
                            "*Overview: *\n" + vac['overview'] + '\n\n'
                            "" + vac['url'] + ' '
                     )


def set_alert(chat_id, message_id, username):
    try:
        Alert.objects.create(chat_id=chat_id)
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You've subscribed to vacancy updates.\n"
                          "Now, you'll get all new vacancies available on the web twice a day."
                     )
    except IntegrityError:
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You already subscribed to vacancy updates.\n"
                          "Send /unsetalert if you want to unsubscribe."
                     )
    finally:
        try:
            User.objects.update_or_create(chat_id=chat_id, defaults={'username': username})
        except IntegrityError:
            pass


def help(chat_id, message_id):
    message = send_message(chat_id=chat_id,
                             reply_to_message_id=message_id,
                             text="*How to use IT Vacancies bot?\n\n*"
                                  "*This bot connects to popular vacancy websites and parses all new IT vacancies available.\n"
                                  "So, you don't have to manually check websites every time.\n\n*"
                                  "Here are the control commands of the bot:\n"
                                  "/start - Starts the bot and automatically subscribe you to the twice-daily vacancy updates.\n"
                                  "/vacancy - Get a random vacancy from all available vacancies for the past week.\n"
                                  "/setalert - Subscribe to the twice-daily vacancy updates. So, you'll get all new vacancies available every 12 hours.\n"
                                  "/unsetalert - Unsubscribe from twice-daily vacancy updates. You'll no longer get vacancy notifications.\n"
                                  "/help - You'll get this help message.\n\n"
                                  "_Note: This bot only works with Azerbaijan vacancy websites._\n\n"
                                  "*GitHub repo:* https://github.com/mesolaries/itvac-telegram-bot"
                 )
    return message


def unset_alert(chat_id, message_id):
    try:
        Alert.objects.filter(chat_id=chat_id).delete()
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You've unsubscribed from vacancy updates.\n"
                          "You'll no longer get alerts about new vacancies available.\n"
                          "Send /setalert if you want to get them again."
                     )
    except:
        pass


# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class CommandReceiveView(View):
    def get(self, request):
        return HttpResponse("Hello! This is @itvac_bot telegram bot!")

    def post(self, request):
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

        return HttpResponse(status=200)
