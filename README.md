# IT Vacancies Telegram bot
This bot scrapes data from job websites and sends IT vacancies to the user.

The bot built with [Telegram Bot API](https://core.telegram.org/bots/api) and [Python3](https://www.python.org/).

It uses [SQLite](https://www.sqlite.org/) database to store chat IDs of users.
So, the bot can send job alerts to users.

The bot is based on [webhook](https://en.wikipedia.org/wiki/Webhook) technology.
That's why I used [Django](https://www.djangoproject.com/) to wrap all project and handle webhook requests.

## Supported websites
The bot supports 3 popular vacancy websites for now.
- [x] http://www.rabota.az/
- [x] https://boss.az/
- [x] https://jobs.day.az/

**TODO**
- [ ] http://jobsearch.az/

## How you can use this repo?
You can easily use this repo to scrape any data from any website and send scraped data to users.

You just need to change URLs and Class names in `vacancies.py` file.

Then, scrape data in `vacancies()` method using [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4).

___

IT Vacancies bot: https://t.me/itvac_bot

Join my IT Vacancies channel: https://t.me/it_vacancies
