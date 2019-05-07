import requests

url = 'https://api.hh.ru/vacancies'

vacancies_count = {}

#language_list = ['python', 'java', 'Javascript','TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby']
language_list = ['python']

for language in language_list:
  headers = {
    'User-Agent': 'HH-User-Agent'
    }
  params = {
    'area': 1,
    'text': 'программист' + language
  }
  response = requests.get(url, headers=headers, params=params)
  #print(response.url)
  json_response = response.json()
  vacancies_count.update({language : json_response['found']})
  for item in json_response['items']:
    #print(item['salary'])
    
    if (item['salary'] is not None) and (item['salary']['currency'] == 'RUR'):
      if (item['salary']['from'] is not None) and (item['salary']['to'] is not None):
        print((item['salary']['from']+item['salary']['to'])/2)
      elif (item['salary']['from'] is not None):
        print(item['salary']['from'] * 2)
      elif (item['salary']['to'] is not None):
        print(item['salary']['to'] * 0.8)
    else:
      print('None')
    
      
#print(vacancies_count)
