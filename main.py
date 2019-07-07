import requests
import json
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


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

#---------------------hh.ru:---------------------
def get_hh_statistic_dict(language_list):
  hh_url = 'https://api.hh.ru/vacancies'
  middle_language_price_hh = {}
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
      #print('Download {}, page {}/{}'.format(language, page, pages_number))
      for vacancy in page_data['items']:
        if get_predict_rub_salary_hh(vacancy) is not None:
          vacancies_processed += 1
          #print('vacancies_processed = {}, salary = {}, sum = {}'.format(vacancies_processed, get_predict_rub_salary_hh(vacancy), summary_salary))
          summary_salary = int(summary_salary + get_predict_rub_salary_hh(vacancy))
          average_salary = int(summary_salary / vacancies_processed)
          middle_language_price_hh[language] = {
            'vacancies_found': page_data['found'],
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
          }
  #print(json.dumps(middle_language_price_hh, indent=4, sort_keys=True))
  return middle_language_price_hh

#--------------------superjob:---------------------
def get_sj_statistic_dict(language_list):
  secret_key = os.getenv("SJ_KEY")
  sj_url='https://api.superjob.ru/2.0/vacancies'
  middle_language_price_sj = {}
  for language in language_list:
    page = 0
    vacancies_processed = 0
    average_salary = 0
    summary_salary = 0
    next_page = True
    while (next_page):
      headers = {
        'X-Api-App-Id': secret_key
      }
      params = {
        'page': page, #Номер страницы результата поиска
        'count': 5, #Количество результатов на страницу поиска
        'keyword': language,
        'town': 4, #Название города или его ID. 4 - Москва
        'catalogues': 48, #Список разделов каталога отраслей. Список значений можно узнать из метода catalogues, параметр key в любом объекте. 48 - "Разработка, программирование"
        'no_agreement': 1 #Без вакансий, где оклад по договоренности
      }
      page_data = requests.get(sj_url, headers=headers, params=params).json()
      next_page = page_data['more']
      page = page + 1
      #print('Download {}, page {}'.format(language, page))
      for vacancy in page_data['objects']:
        vacancies_processed += 1
        #print('{}, {}: {}-{} ({}) {}'.format(vacancy['profession'], vacancy['town']['title'], vacancy['payment_from'], vacancy['payment_to'], get_predict_rub_salary_sj(vacancy), vacancy['currency']))
        summary_salary = int(summary_salary + get_predict_rub_salary_sj(vacancy))
        average_salary = int(summary_salary / vacancies_processed)
        middle_language_price_sj[language] = {
          'vacancies_found': page_data['total'],
          'vacancies_processed': vacancies_processed,
          'average_salary': average_salary
        }
  #print(json.dumps(middle_language_price_sj, indent=4, sort_keys=True))
  return middle_language_price_sj

def table_output(title, statistic_dict):
  TABLE_DATA = [['lang', 'vacancies_found', 'vacancies_processed', 'average_salary']]
  for main_key, main_value in statistic_dict.items():
    row=[]
    row.append(main_key)
    for key, value in main_value.items():
      row.append(value)
    TABLE_DATA.append(row)
  table_instance = AsciiTable(TABLE_DATA, title)
  return table_instance.table

if __name__ == "__main__":
  #language_list = ['Python', 'Java', 'Javascript','TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby', 'c++', 'c#', '1c']
  language_list = ['PHP']
  
  title = '--------------------HH statistics'
  print(table_output(title, get_hh_statistic_dict(language_list)))
  
  title = '--------------------SJ statistics'
  print(table_output(title, get_sj_statistic_dict(language_list)))
