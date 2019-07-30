import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from > 0 and salary_to > 0:
        mid_salary = int((salary_from + salary_to) / 2)
    elif salary_from > 0:
        mid_salary = int(salary_from * 1.2)
    elif salary_to > 0:
        mid_salary = int(salary_to * 0.8)
    return mid_salary


def predict_rub_salary_hh(vacancy):
    hh_rub_salary = 0
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        salary_from = vacancy['salary']['from'] or 0
        salary_to = vacancy['salary']['to'] or 0
        hh_rub_salary = predict_salary(salary_from, salary_to)
    return hh_rub_salary


def predict_rub_salary_sj(vacancy):
    sj_predict_salary = 0
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    if vacancy['currency'] == 'rub':
        sj_predict_salary = predict_salary(salary_from, salary_to)
    return sj_predict_salary


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
            headers = {'User-Agent': 'HH-User-Agent'}
            params = {
                'area': 1, # Код города, 1 - Москва
                'text': 'программист ' + language,
                'page': page # Страница поиска
            }
            page_request = requests.get(hh_url, headers=headers, params=params)
            page += 1
            if check_request(page_request):
                answer = page_request.json()
                page_data.append(answer['items'])
                pages_number = answer['pages']
        for vacancies in page_data:
            for vacancy in vacancies:
                if predict_rub_salary_hh(vacancy):
                    vacancies_processed += 1
                    summary_salary = int(summary_salary +
                                         predict_rub_salary_hh(vacancy))
                    average_salary = int(summary_salary / vacancies_processed)
                    middle_language_price_hh[language] = {
                        'vacancies_found': answer['found'],
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
        page_data = []
        vacancies_processed = 0
        summary_salary = 0
        next_page = True
        while next_page:
            headers = {'X-Api-App-Id': secret_key}
            params = {
                'page': page,  # Номер страницы результата поиска
                'count': 5,  # Количество результатов на страницу поиска
                'keyword': language, # Язык программирования
                'town': 4,  # Название города или его ID. 4 - Москва
                'catalogues': 48,  # Список разделов каталога отраслей. 48 - "Разработка, программирование"
                'no_agreement': 1  # Без вакансий, где оклад по договоренности
            }
            page_request = requests.get(sj_url, headers=headers, params=params)
            if check_request(page_request):
                answer = page_request.json()
                page_data.append(answer['objects'])
                next_page = answer['more']
                page = page + 1
            else:
                next_page = False
        for vacancies in page_data:
            for vacancy in vacancies:
                vacancies_processed += 1
                summary_salary = int(summary_salary +
                                     predict_rub_salary_sj(vacancy))
                average_salary = int(summary_salary / vacancies_processed)
                middle_language_price_sj[language] = {
                    'vacancies_found': answer['total'],
                    'vacancies_processed': vacancies_processed,
                    'average_salary': average_salary
                }
    return middle_language_price_sj


def make_table(site_name, statistic_dict):
    title = '-----------------{} statistics'.format(site_name)
    if statistic_dict:
        table_data = [[
            'lang', 'vacancies_found', 'vacancies_processed', 'average_salary'
        ]]
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
    # language_list = ['Python', 'Java', 'Javascript', 'TypeScript', 'Swift',
    #                'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'PHP', 'Ruby', 'c++', 'c#',#  '1c']
    language_list = ['Python']
    site_name = 'HH'
    print(make_table(site_name, get_hh_statistic(language_list)))

    site_name = 'SJ'
    print(make_table(site_name, get_sj_statistic_dict(language_list)))
