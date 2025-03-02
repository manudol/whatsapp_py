import json

class GetMessages:
    def __init__(self, file_path: str):
        self.file_path = file_path


    def get_json(self):
        with open(self.file_path, 'r') as f: 
            json_data = json.load(f)
            if len(json_data['messages']) == 0:
                return None
            elif len(json_data['messages']) <= 20:
                return json_data['messages']
            else: return json_data['messages'][-20:]

    