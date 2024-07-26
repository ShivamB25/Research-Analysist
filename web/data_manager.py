import json

class DataManager:
    def __init__(self):
        self.data = {}

    def set_scraped_content(self, content):
        self.data['scraped_content'] = content

    def save_data(self):
        with open('scraped_data.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)