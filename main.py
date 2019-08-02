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


def get_vacancies_from_hh(language):
    hh_url = 'https://api.hh.ru/vacancies'
    page = 0  # первая страница поиска (нумерация с 0)
    number_of_pages = 1
    vacancies_data = []
    while page < number_of_pages:
        headers = {'User-Agent': 'HH-User-Agent'}
        params = {
            'area': 1,  # Код города, 1 - Москва
            'text': 'программист ' + language,
            'page': page  # Текущая страница поиска
        }
        response = requests.get(hh_url, headers=headers, params=params)
        if check_request(response):
            response_data = response.json()
            vacancies_data.extend(response_data['items'])

            number_of_pages = response_data['pages'] - 1
            # print('Download {} pages: {}/{}'.format(language, page, number_of_pages))
            page += 1
    number_of_vacancies = response_data['found']
    return [vacancies_data, number_of_vacancies]


def get_hh_statistic(vacancies):
    vacancies_processed = 0
    hh_statistics = {}
    summary_salary = 0
    number_of_vacancies = vacancies[1]
    for vacancy in vacancies[0]:
        if predict_rub_salary_hh(vacancy):
            vacancies_processed += 1
            summary_salary = int(summary_salary + predict_rub_salary_hh(vacancy))
            average_salary = int(summary_salary / vacancies_processed)
            hh_statistics = {
                'vacancies_found': number_of_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    return hh_statistics


def make_all_language_stat_from_hh(language_list):
    stat = {}
    for language in language_list:
        vacancies = get_vacancies_from_hh(language)
        stat[language] = get_hh_statistic(vacancies)
    return stat


def get_vacancies_from_sj(language):
    secret_key = os.getenv('SJ_KEY')
    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    page = 0
    next_page = True
    vacancies_data = []
    while next_page:
        headers = {'X-Api-App-Id': secret_key}
        params = {
            'page': page,  # Номер страницы результата поиска
            'count': 5,  # Количество результатов на страницу поиска
            'keyword': language,  # Язык программирования
            'town': 4,  # Название города или его ID. 4 - Москва
            'catalogues': 48,  # Список разделов каталога отраслей. 48 - "Разработка, программирование"
            'no_agreement': 1  # Без вакансий, где оклад по договоренности
        }
        response = requests.get(sj_url, headers=headers, params=params)
        if check_request(response):
            response_data = response.json()
            vacancies_data.extend(response_data['objects'])
            next_page = response_data['more']
            # print('Download {} pages: {}'.format(language, page))
            page += 1
        else:
            next_page = False
    number_of_vacancies = response_data['total']
    # print(number_of_vacancies)
    return [vacancies_data, number_of_vacancies]


def get_sj_statistic(vacancies):
    vacancies_processed = 0
    sj_statistics = {}
    summary_salary = 0
    number_of_vacancies = vacancies[1]
    for vacancy in vacancies[0]:
        vacancies_processed += 1
        summary_salary = int(summary_salary + predict_rub_salary_sj(vacancy))
        average_salary = int(summary_salary / vacancies_processed)
        sj_statistics = {
            'vacancies_found': number_of_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    return sj_statistics


def make_all_language_stat_from_sj(language_list):
    stat = {}
    for language in language_list:
        vacancies = get_vacancies_from_sj(language)
        stat[language] = get_sj_statistic(vacancies)
    return stat


def make_table(site_name, statistic_dict):
    title = '-----------------{} statistics'.format(site_name)
    if statistic_dict:
        table_data = [[
            'lang', 'vacancies_found', 'vacancies_processed', 'average_salary'
        ]]
        for language, language_stat in statistic_dict.items():
            if language_stat:
                row = [language]
                for key, value in language_stat.items():
                    row.append(value)
                table_data.append(row)
        return AsciiTable(table_data, title).table
    else:
        return 'No data was found'


if __name__ == "__main__":
    load_dotenv()
    language_list = ['Python', 'Java', 'Javascript', 'TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C',
                     'PHP', 'Ruby', 'c++', 'c#', '1c']
    site_name = 'HH'
    print(make_table(site_name, make_all_language_stat_from_hh(language_list)))

    site_name = 'SJ'
    print(make_table(site_name, make_all_language_stat_from_sj(language_list)))
