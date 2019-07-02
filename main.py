import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def is_none(param):
  if param is None:
    return 0
  else:
    return param

def get_predict_salary(salary_from, salary_to):
  if (salary_from > 0) and (salary_to > 0):
    return int((salary_from + salary_to)/2)
  elif (salary_from > 0):
    return int(salary_from * 1.2)
  elif (salary_to > 0):
    return int(salary_to * 0.8)
  else:
    return None

def get_predict_rub_salary_hh(vacancy):
  if (vacancy['salary'] is not None) and (vacancy['salary']['currency'] == 'RUR'):
    #print('salary_from: {},  salary_to: {}'.format(salary_from, salary_to))
    salary_from = is_none(vacancy['salary']['from'])
    salary_to = is_none(vacancy['salary']['to'])
    return get_predict_salary(salary_from, salary_to)
  return None

def get_predict_rub_salary_sj(vacancy):
  salary_from = vacancy['payment_from']
  salary_to = vacancy['payment_to']
  if (vacancy['currency'] == 'rub'):
    return get_predict_salary(salary_from, salary_to)
  else:
    return None

'''
#---------------------hh.ru:---------------------
hh_url = 'https://api.hh.ru/vacancies'
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
    page_data = requests.get(hh_url, headers=headers, params=params).json()
    pages_number = page_data['pages']
    page += 1
    print('Download {}, page {}/{}'.format(language, page, pages_number))
    for vacancy in page_data['items']:
      if get_predict_rub_salary_hh(vacancy) is not None:
        vacancies_processed += 1
        print('vacancies_processed = {}, salary = {}, sum = {}'.format(vacancies_processed, get_predict_rub_salary_hh(vacancy), summary_salary))
        summary_salary = int(summary_salary + get_predict_rub_salary_hh(vacancy))
        average_salary = int(summary_salary / vacancies_processed)
  middle_language_price[language] = {
    'vacancies_found': page_data['found'],
    'vacancies_processed': vacancies_processed,
    'average_salary': average_salary
    }

print(json.dumps(middle_language_price, indent=4, sort_keys=True))
'''

#--------------------superjob:---------------------
secret_key = os.getenv("SJ_KEY")
sj_url='https://api.superjob.ru/2.0/vacancies'
headers = {
  'X-Api-App-Id': secret_key
}
params = {
  'page': 5, #Номер страницы результата поиска
  'count': 100, #Количество результатов на страницу поиска
  'town': 4, #Название города или его ID. 4 - Москва
  'catalogues': 48, #Список разделов каталога отраслей. Список значений можно узнать из метода catalogues, параметр key в любом объекте
  'no_agreement': 1 #не показывать оклад по договоренности
}

#response = requests.get(sj_url, headers=headers, params=params)
#print(response.url)
#print(response.json())
#vacancy['profession'] == 'Программист'
#vacancy['town']['id'] == 4
#vacancy['catalogues'][0]['positions'][0]['key'] == 48

page_data = requests.get(sj_url, headers=headers, params=params).json()
print(page_data['more'])
i=0
for vacancy in page_data['objects']:
  i+=1
  print('{}) {}, {}: {}-{} ({}) {}'.format(i, vacancy['profession'], vacancy['town']['title'], vacancy['payment_from'], vacancy['payment_to'], get_predict_rub_salary_sj(vacancy), vacancy['currency']))
'''
  for vacancy in page_data['objects']:
    #print (vacancy['catalogues'][0]['id']);
    if vacancy['catalogues'][0]['id'] == 438:
      print('{}, {} - {}'.format(vacancy['profession'], vacancy['town']['title'], vacancy['catalogues'][0]['positions'][0]['key']))
#print(page_data['objects'])
#print(page_data.text)
'''
