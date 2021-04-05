import requests
from pathlib import Path
import json
import time


class Parse5ka:
    headers = {
        "User-Agent": "Undefined"
    }

    def __init__(self, special_offers_url: str, categories_url: str,  save_path: Path):
        self.special_offers_url = special_offers_url
        self.categories_url = categories_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def _get_categories(self):
        return self._get_response(self.categories_url).json()

    def run_category(self):
        for category in self._get_categories():
            category['products'] = []
            category['products'].extend(list(
                self._parse(f'{self.special_offers_url}?categories={category["parent_group_code"]}')))
            self._save(category, self.save_path.joinpath(f'{category["parent_group_code"]}.json'))

    def run_products(self):
        for product in self._parse(self.start_url):
            product_path = self.save_path.joinpath(f'{product["id"]}.json')
            self._save(product, product_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data.get('next')
            for product in data.get('results', []):
                yield product

    def _save(self, data, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == '__main__':
    parser = Parse5ka("https://5ka.ru/api/v2/special_offers/",
                      "https://5ka.ru/api/v2/categories/",
                      get_save_path('categories'))
    parser.run_category()

