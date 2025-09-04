import csv
import json
import os

def convert_all_csv_to_json(csv_folder_path, json_output_path):
    all_data = []

    # Loop through each CSV file in the folder
    for filename in os.listdir(csv_folder_path):
        if filename.endswith(".csv"):
            csv_file_path = os.path.join(csv_folder_path, filename)

            with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if "Text" in row and "Label" in row:
                        all_data.append({
                            "text": row["Text"].strip(),                                        
                            "label": row["Label"].strip()
                        })
                    else:
                        print(f"⚠️ Missing 'Text' or 'Label' in {filename}")

            print(f"✅ Processed {filename}")

    # Save all combined data into one JSON file
    with open(json_output_path, mode='w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=2, ensure_ascii=False)

    print(f"\nCombined {len(all_data)} entries into: {json_output_path}")

# Example usage
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))  # go up from utils/
    csv_folder = os.path.join(base_dir, "training_csv")
    json_output = os.path.join("ai_model", "SOS-Ai-TrainingData.json")

    convert_all_csv_to_json(csv_folder, json_output)
