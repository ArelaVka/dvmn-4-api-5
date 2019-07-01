import requests
import json


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

language_list = ['python', 'java', 'Javascript','TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby']

for language in language_list:
  headers = {
    'User-Agent': 'HH-User-Agent'
    }
  params = {
    'area': 1,
    'text': 'программист' + language
  }
  response = requests.get(url, headers=headers, params=params)
  json_response = response.json()

  
  vacancies_processed = 0
  average_salary = 0

  for vacancy in json_response['items']:
    if predict_rub_salary(vacancy) is not 'None':
      vacancies_processed += 1
      average_salary = int((average_salary + predict_rub_salary(vacancy)) / 2
  middle_language_price[language] = {'vacancies_found': json_response['found'], 'vacancies_processed': vacancies_processed, 'average_salary': average_salary}

print(json.dumps(middle_language_price, indent=4, sort_keys=True))
