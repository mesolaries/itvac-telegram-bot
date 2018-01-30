import requests, os

token = os.environ.get('TOKEN')
base_url = "https://api.telegram.org/bot{}/".format(token)


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
