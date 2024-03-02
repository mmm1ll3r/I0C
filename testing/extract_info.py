import os
import json
import csv

def extract_data(folder_path, output_csv="extracted_data2.csv"):
    rows = [["Filename", "Families", "Malware Names", "Filetype Tags"]]  # Header for CSV
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path) as file:
                data = json.load(file)
                families = get_families(data)
                malware_names = get_malware_names(data)
                filetype_tags = get_filetype_tags(data)
                rows.append([filename, ", ".join(families) if families else "None", ", ".join(malware_names) if malware_names else "None", ", ".join(filetype_tags) if filetype_tags else "None"])

    # Write to CSV
    with open(output_csv, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(rows)

    print("Data saved to", output_csv)

def get_families(data):
    families = []
    attributes = data.get("attributes", {})
    malware_config = attributes.get("malware_config", {})
    families_info = malware_config.get("families", [])
    for family_info in families_info:
        family_name = family_info.get("family")
        if family_name:
            families.append(family_name)
    return families

def get_malware_names(data):
    malware_names = []
    attributes = data.get("attributes", {})
    sandbox_verdicts = attributes.get("sandbox_verdicts", {})
    for verdict in sandbox_verdicts.values():
        malware_names.extend(verdict.get("malware_names", []))
    return malware_names

def get_filetype_tags(data):
    attributes = data.get("attributes", {})
    type_tags = attributes.get("type_tags", [])
    return type_tags

folder_path = "./20240218_40"
extract_data(folder_path)