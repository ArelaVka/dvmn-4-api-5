import requests

url = 'https://api.hh.ru/vacancies'
headers = {
    'User-Agent': 'HH-User-Agent'
}
response = requests.get(url, headers=headers)
print(response.json())
