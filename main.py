import requests
import json
from itertools import count


def predict_rub_salary(vacancy):
  if (vacancy['salary'] is not None) and (vacancy['salary']['currency'] == 'RUR'):
      if (vacancy['salary']['from'] is not None) and (vacancy['salary']['to'] is not None):
        return int((vacancy['salary']['from']+vacancy['salary']['to'])/2)
      elif (vacancy['salary']['from'] is not None):
        return int(vacancy['salary']['from'] * 2)
      elif (vacancy['salary']['to'] is not None):
        return int(vacancy['salary']['to'] * 0.8)
  else:
    return 'None'


url = 'https://api.hh.ru/vacancies'
middle_language_price = {}

language_list = ['Python', 'Java', 'Javascript','TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby']
#language_list = ['Python']

for language in language_list:
  page = 0
  pages_number = 1

  headers = {
    'User-Agent': 'HH-User-Agent'
  }
  params = {
    'area': 1,
    'text': 'программист' + language,
    'page': page
  }

  vacancies_processed = 0
  average_salary = 0
  summary_salary = 0
  while page < pages_number:
    page_data = requests.get(url, headers=headers, params=params).json()
    pages_number = page_data['pages']
    page += 1
    print('PAGE {}'.format(page))
    for vacancy in page_data['items']:
      if predict_rub_salary(vacancy) is not 'None':
        vacancies_processed += 1
        summary_salary = int(summary_salary + predict_rub_salary(vacancy))
    average_salary = int(summary_salary / vacancies_processed)
  middle_language_price[language] = {'vacancies_found': page_data['found'], 'vacancies_processed': vacancies_processed, 'average_salary': average_salary}

  print(json.dumps(middle_language_price, indent=4, sort_keys=True))
