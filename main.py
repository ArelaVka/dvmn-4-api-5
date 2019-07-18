import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def get_predict_salary(salary_from, salary_to):
    if (salary_from > 0) and (salary_to > 0):
        return int((salary_from + salary_to) / 2)
    elif salary_from > 0:
        return int(salary_from * 1.2)
    elif salary_to > 0:
        return int(salary_to * 0.8)
    else:
        return None


def get_predict_rub_salary_hh(vacancy):
    if (vacancy['salary']) and (vacancy['salary']['currency'] == 'RUR'):
        salary_from = (vacancy['salary']['from']) or 0
        salary_to = (vacancy['salary']['to']) or 0
        return get_predict_salary(salary_from, salary_to)
    return None


def get_predict_rub_salary_sj(vacancy):
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    if vacancy['currency'] == 'rub':
        return get_predict_salary(salary_from, salary_to)
    else:
        return None


def check_request(request):
    try:
        request.raise_for_status()
        return request
    except requests.exceptions.HTTPError as error:
        print('ERROR: {}'.format(error))
        return None


def get_hh_statistic(language_list):
    hh_url = 'https://api.hh.ru/vacancies'
    middle_language_price_hh = {}
    for language in language_list:
        page_data = []
        page = 0
        pages_number = 1
        vacancies_processed = 0
        summary_salary = 0
        while page < pages_number:
            headers = {
                'User-Agent': 'HH-User-Agent'
            }
            params = {
                'area': 1,
                'text': 'программист ' + language,
                'page': page
            }
            page_request = requests.get(hh_url, headers=headers, params=params)
            page += 1
            if check_request(page_request):
                page_data.append(page_request.json()['items'])
                pages_number = page_request.json()['pages']
        for vacancies in page_data:
            for vacancy in vacancies:
                if get_predict_rub_salary_hh(vacancy):
                    vacancies_processed += 1
                    summary_salary = int(summary_salary + get_predict_rub_salary_hh(vacancy))
                    average_salary = int(summary_salary / vacancies_processed)
                    middle_language_price_hh[language] = {
                        'vacancies_found': page_request.json()['found'],
                        'vacancies_processed': vacancies_processed,
                        'average_salary': average_salary
                    }
    return middle_language_price_hh


def get_sj_statistic_dict(language_list):
    secret_key = os.getenv("SJ_KEY")
    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    middle_language_price_sj = {}
    for language in language_list:
        page = 0
        vacancies_processed = 0
        summary_salary = 0
        next_page = True
        while next_page:
            headers = {
                'X-Api-App-Id': secret_key
            }
            params = {
                'page': page,  # Номер страницы результата поиска
                'count': 5,  # Количество результатов на страницу поиска
                'keyword': language,
                'town': 4,  # Название города или его ID. 4 - Москва
                'catalogues': 48,  # Список разделов каталога отраслей. 48 - "Разработка, программирование"
                'no_agreement': 1  # Без вакансий, где оклад по договоренности
            }
            page_data = requests.get(sj_url, headers=headers, params=params)
            if check_request(page_data):
                page_json_data = page_data.json()
                next_page = page_json_data['more']
                page = page + 1
                for vacancy in page_json_data['objects']:
                    vacancies_processed += 1
                    summary_salary = int(summary_salary + get_predict_rub_salary_sj(vacancy))
                    average_salary = int(summary_salary / vacancies_processed)
                    middle_language_price_sj[language] = {
                        'vacancies_found': page_json_data['total'],
                        'vacancies_processed': vacancies_processed,
                        'average_salary': average_salary
                    }
            else:
                next_page = False
    return middle_language_price_sj


def make_table(site_name, statistic_dict):
    title = '-----------------{} statistics'.format(site_name)
    if statistic_dict:
        table_data = [['lang', 'vacancies_found', 'vacancies_processed', 'average_salary']]
        for language, language_stat in statistic_dict.items():
            row = [language]
            for key, value in language_stat.items():
                row.append(value)
            table_data.append(row)
        return AsciiTable(table_data, title).table
    else:
        return 'No data was found'


if __name__ == "__main__":
    load_dotenv()
    language_list = ['Python', 'Java', 'Javascript', 'TypeScript', 'Swift',
                     'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby', 'c++', 'c#', '1c']
    site_name = 'HH'
    print(make_table(site_name, get_hh_statistic(language_list)))

    site_name = 'SJ'
    print(make_table(site_name, get_sj_statistic_dict(language_list)))
