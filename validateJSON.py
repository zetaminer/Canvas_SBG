import json

json_file = "quiz_data.json"

try:
    with open(json_file, "r") as file:
        data = json.load(file)
    print("✅ JSON is valid!")
except json.JSONDecodeError as e:
    print(f"❌ JSON Decode Error: {e}")
