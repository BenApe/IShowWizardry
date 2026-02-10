import json

class jsonutils():
    def loadjson(file_name:str):
        file_path = f"{file_name}.json"
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                if isinstance(data, dict):
                    data = {
                        key: value
                        for key, value in data.items()
                    }
                    
        except Exception as e:
            print(f"Error loading file {file_path}: {e}. Starting with an empty file.")
            
        return data
    
    def savejson(file_name, data):
        file_path = f"{file_name}.json"
        
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
                
        except Exception as e:
            print(f"Error saving {file_path}: {e}")