"""
This module parses data from websites.
To add new website or edit existing one, create/edit __WebsiteName Class and its methods.
You need to set new url to parse new website.
Each website has its own structure. So, each website parsing is unique.

Use get_new_vacancies() method to get parsed data.
get_random_vacancy() method returns a random data from get_new_vacancies().
"""

import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz


def get_new_vacancies():
    rabota_az = __RabotaAz()
    day_az = __DayAz()
    boss_az = __BossAz()
    # Sum of all vacancies available
    vacancies = rabota_az.vacancies() + day_az.vacancies() + boss_az.vacancies()
    return vacancies


def get_random_vacancy(count=1):
    websites = [__RabotaAz, __DayAz, __BossAz]
    # Get a random website and parse vacancies from there
    random_website = random.choice(websites)  # class instance
    random_website = random_website()  # reassign and initializing class
    random_vacancy = random_website.random()  # calling random method of the class
    if random_vacancy == {}:  # If no random vac, try again
        if count < 5:  # preventing infinite recursion
            return get_random_vacancy(count=count+1)
    return random_vacancy


class __RabotaAz:
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    url_daily = "http://www.rabota.az/vacancy/search/?sortby=3&created=1&category%5B%5D=6"
    url_weekly = "http://www.rabota.az/vacancy/search/?sortby=3&created=7&category%5B%5D=6"
    base_url = "http://www.rabota.az"

    def vacancies(self, url=url_daily):
        page = requests.get(url,
                            headers={
                                'User-agent': self.user_agent
                            }
                            )
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'lxml')
            data = {'results': []}
            try:
                vacancies = soup.find('ul', {'class': 'visitor-vacancy-list'}).find_all('li')
            except AttributeError:
                return data['results']
            for vacancy in vacancies:
                title = vacancy.find('a', {'class': 'title-'}).h2.get_text()
                salary = vacancy.find('b', {'class': 'salary-'}).get_text()
                location = vacancy.find('b', {'class': 'address-'}).get_text()
                company = vacancy.find('span', {'class': 'company-'}).b.get_text()
                overview = vacancy.find_all('p')[-1].get_text()  # Overview is in the last <p>
                overview = overview.replace("\t", '')[1:]  # [1:0] removes new line at the beginning
                url = self.base_url + vacancy.find('a', {'class': 'title-'}).get('href')
                data['results'].append(
                    {
                        "title": title, "salary": salary, "location": location,
                        "company": company, "overview": overview, "url": url
                    }
                )
            return data['results'][::-1]  # Newest vacancy comes last
        else:
            return []

    def random(self):
        vacancies = self.vacancies(url=self.url_weekly)
        try:
            random_vacancy = random.choice(vacancies)
        except (IndexError, ValueError):
            random_vacancy = {}
        return random_vacancy


class __DayAz:
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    url_daily = "https://jobs.day.az/catalog/Informacionnye-tehnologii-Internet-Telekom?search_period=1&specialization=1"
    url_weekly = "https://jobs.day.az/catalog/Informacionnye-tehnologii-Internet-Telekom?search_period=7&specialization=1"
    base_url = "https://jobs.day.az/locale?language=EN"  # Get website in english

    def vacancies(self, url=url_daily):
        session = requests.Session()
        session.get(self.base_url, headers={'User-agent': self.user_agent})
        page = session.get(url,
                           headers={
                               'User-agent': self.user_agent
                           }
                           )
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'lxml')
            data = {'results': []}
            try:
                vacancies = soup.find('div', {'class': 'vacancy-serp'}).find_all('div', {'class': 'vacancy-serp-item'})
            except AttributeError:
                return data['results']
            for vacancy in vacancies:
                title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get_text()
                try:
                    salary = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-compensation'}).get_text()
                except:
                    salary = "-"
                location = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).get_text()
                company = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).get_text()
                requirements = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).get_text()
                responsibility = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).get_text()
                overview = requirements + '\n' + responsibility
                url = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
                data['results'].append(
                    {
                        "title": title, "salary": salary, "location": location,
                        "company": company, "overview": overview, "url": url
                    }
                )
            return data['results'][::-1]  # Newest vacancy comes last
        else:
            return []

    def random(self):
        vacancies = self.vacancies(url=self.url_weekly)
        try:
            random_vacancy = random.choice(vacancies)
        except (IndexError, ValueError):
            random_vacancy = {}
        return random_vacancy


class __BossAz:
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    # No daily/weekly filter on website
    url = "https://en.boss.az/vacancies?search%5Bcategory_id%5D=38"
    base_url = "https://en.boss.az"

    def vacancies(self, url=url, offset=0):  # offset - vacancy post date period (e.g. 7 = for the past week, 0 - today)
        page = requests.get(url, headers={'User-agent': self.user_agent})
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'lxml')
            data = {'results': []}
            try:
                now = datetime.now(pytz.timezone('Asia/Baku'))
                today = now.date()
                all_vacancies = soup.find_all('div', {'class': 'results-i'})
                count = 0
                for vac in all_vacancies:
                    link = vac.find('a', {'class': 'results-i-link'}).get('href')
                    inner_vac = requests.get(self.base_url + link, headers={'User-agent': self.user_agent})
                    inner_soup = BeautifulSoup(inner_vac.content, 'lxml')
                    vac_date = inner_soup.find('div', {'class': 'bumped_on params-i-val'}).get_text()
                    vac_date = datetime.strptime(vac_date, "%B %d, %Y").date()
                    #  Count vacancy if it's in a given time period (offset)
                    if today <= vac_date + timedelta(days=offset):
                        count += 1
                    else:
                        break
                vacancies = all_vacancies[:count]
            except AttributeError:
                return data['results']
            for vacancy in vacancies:
                title = vacancy.h3.get_text()
                salary = vacancy.find('div', {'class': 'results-i-salary'}).get_text()
                location = str(vacancy.find('div', {'class': 'results-i-secondary'}).contents[0])
                company = vacancy.find('a', {'class': 'results-i-company'}).get_text()
                overview = vacancy.find('div', {'class': 'results-i-summary'}).p.get_text()
                url = self.base_url + vacancy.find('a', {'class': 'results-i-link'}).get('href')
                data['results'].append(
                    {
                        "title": title, "salary": salary, "location": location,
                        "company": company, "overview": overview, "url": url
                    }
                )
            return data['results'][::-1]
        else:
            return []

    def random(self):
        vacancies = self.vacancies(url=self.url, offset=7)
        try:
            random_vacancy = random.choice(vacancies)
        except (IndexError, ValueError):
            random_vacancy = {}
        return random_vacancy
