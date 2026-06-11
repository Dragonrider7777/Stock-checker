from utils.json_utils import load_json, save_json

def add_to_history(filename, result):
    history = load_json(filename, [])
    history.append(result)
    save_json(filename, history)