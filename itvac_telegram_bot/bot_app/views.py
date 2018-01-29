# from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import re
import json

from bot_app.models import User, Reminder
from bot_app.reminder.vacancies import get_random_vacancy
from bot_app.reminder.message import send_message


# Handlers
def start(chat_id, username):
    response = send_message(chat_id,
                            text="Hi! I'm IT Vacancies Bot.\n"
                                 "I'll send you updates about new IT vacancies available on the a web twice a day.\n"
                                 "Send _/cancel_ to stop receiving the updates."
                            )
    try:
        # Create object if doesn't exist. Update username if changed.
        User.objects.update_or_create(chat_id=chat_id, defaults={'username': username})
    except IntegrityError:
        pass
    finally:
        try:
            Reminder.objects.create(chat_id=chat_id)
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


def reminder(chat_id, message_id, username):
    try:
        Reminder.objects.create(chat_id=chat_id)
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You've subscribed to vacancy updates.\n"
                          "Now, you'll get all new vacancies available on the web twice a day.\n"
                          "Send _/cancel_, if you want to unsubscribe."
                     )
    except IntegrityError:
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You already subscribed to vacancy updates.\n"
                          "Send _/cancel_ to unsubscribe."
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
                      "Here're the control commands of the bot:\n"
                      "/start - Starts the bot and automatically subscribe you to the twice-daily vacancy updates.\n"
                      "/vacancy - Get 1 random vacancy from all available vacancies for the past week.\n"
                      "/reminder - Subscribe to the twice-daily vacancy updates. So, you'll get all new vacancies available every 12 hours.\n"
                      "/cancel - Unsubscribe from twice-daily vacancy updates. You'll no longer get vacancy notifications.\n"
                      "/help - You'll get this help message.\n\n"
                      "_Note: This bot only works with Azerbaijan vacancy websites._\n\n"
                      "*GitHub repo:* https://github.com/mesolaries/itvac-telegram-bot"
                 )
    return message

def cancel(chat_id, message_id):
    try:
        Reminder.objects.filter(chat_id=chat_id).delete()
        send_message(chat_id,
                     reply_to_message_id=message_id,
                     text="You've unsubscribed from vacancy updates.\n"
                          "Send _/reminder_ to resubscribe."
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
        elif command == '/cancel':
            cancel(chat_id, message_id)
        elif command == '/reminder':
            reminder(chat_id, message_id, username)
        elif command == '/help':
            help(chat_id, message_id)

        return HttpResponse(status=200)
