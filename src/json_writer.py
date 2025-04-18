import json

def save_metadata_json(metadata_list, output_path):
    formatted = {
        "dataResources": []
    }

    for entry in metadata_list:
        formatted["dataResources"].append({
            "patient_id": entry["patient_id"],
            "gestaional_age": entry.get("gestational_age"),
            "demographic_age": entry.get("age"),
            "BMI": entry.get("BMI"),
            "examination_findings": entry.get("findings", [])
        })

    with open(output_path, "w") as f:
        json.dump(formatted, f, indent=4)

    print(f"✅ Saved metadata to {output_path}")
