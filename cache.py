import time
import json
import requests

class Cache:
    def __init__(self):
        pass

    def values_to_str(self, data: dict, string_fields: list) -> dict:
        for field in string_fields:
            if field in data:
                if not isinstance(data[field], str):
                    data[field] = self.round_to_str(data[field])
        return data

    def load_jsonfile(self, path, attempts=5):
        i = 0
        while True:
            i += 1
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception as e:
                if i >= attempts:
                    print(f"{type(e)} Error loading {path}: {e}")
                    return {}
                time.sleep(0.3)

    def download_json(self, url):
        try:
            return requests.get(url).json()
        except Exception as e:
            print(f"{type(e)} Error downloading {url}: {e}")
            return {}

    def save_jsonfile(self, path, data):
        if not isinstance(data, (dict, list)):
            raise TypeError(f"Invalid data type: {type(data)}, must be dict or list")
        try:
            if isinstance(data, (dict, list)):
                with open(path, "w+") as f:
                    json.dump(data, f, indent=4)
                    print(f"Updated {path}")
                    return {"result": f"Updated {path}"}
        except Exception as e:
            print(f"{type(e)} Error saving {path}: {e}")
        return {"error": f"{path} failed to update!"}
