import csv
import json
import os

def convert_csv_to_json(csv_file_path, json_output_path):
    data = []

    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if "Text" in row and "Label" in row:
                data.append({
                    "text": row["Text"].strip(),
                    "label": row["Label"].strip()
                })
            else:
                print("Missing 'Text' or 'Label' column in CSV.")

    with open(json_output_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

    print(f"Converted {len(data)} entries from CSV to JSON at: {json_output_path}")

# Example usage
if __name__ == "__main__":
    # Adjust this to the location of your exported CSV
    csv_input = os.path.join("ai_model", "SOS-Ai-TrainingData-1200.csv") 
    json_output = os.path.join("ai_model", "SOS-Ai-TrainingData.json")
    convert_csv_to_json(csv_input, json_output)
