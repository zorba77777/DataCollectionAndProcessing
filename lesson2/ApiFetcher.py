import requests
import json


class ApiFetcher:

    def save_to_file(self, data: list, f_name: str):
        with open(f_name, 'w') as file:
            file.write(json.dumps(data))

    def fetch_from_api(self, url: str, headers: dict = None) -> dict:
        if headers is None:
            headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        data: dict = response.json()
        return data
