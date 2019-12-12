import requests
import json

user = 'zorba77777'
id = '26170337'
secret = ''

url_base = 'https://api.github.com/'


def save_to_file(data: list, f_name: str):
    with open(f_name, 'w') as file:
        file.write(json.dumps(data))


def fetch_from_api(url: str, headers: dict = None) -> list:
    if headers is None:
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


"""
1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""
url_spec_part = 'users' + '/' + user + '/' + 'repos'
url_full = url_base + url_spec_part

save_to_file(fetch_from_api(url_full), 'git_user_repos')

"""
2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, 
пройдя авторизацию. Ответ сервера записать в файл.
"""
url_spec_part = 'users' + '/' + user + '?' + 'client_id' + '=' + id + '&' + 'client_secret' + '=' + secret
url_full = url_base + url_spec_part

save_to_file(fetch_from_api(url_full), 'response_with_auth')