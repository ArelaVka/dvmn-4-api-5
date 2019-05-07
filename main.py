import requests

url = 'https://api.hh.ru/vacancies'

vacancies_count = {}

language_list = ['python', 'java', 'Javascript']

for language in language_list:
  headers = {
    'User-Agent': 'HH-User-Agent'
    }
  params = {
    'area': 1,
    'text': 'программист' + language
  }
  response = requests.get(url, headers=headers, params=params)
  print(response.url)
  count = response.json()
  vacancies_count.update({language : count['found']})
print(vacancies_count)
