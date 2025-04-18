import os
import pytesseract
import uuid
import json
from pathlib import Path
from src.anonymizer import anonymize_text
from src.extractor import extract_metadata
from src.json_writer import save_metadata_json
from src.pdf_handler import read_pdf_text, write_anonymized_pdf

# Windows-specific path for tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Constants
ID_MAP_FILE = Path("data/id_map.json")

# Load or initialize the secure ID map
if ID_MAP_FILE.exists():
    with open(ID_MAP_FILE, "r") as f:
        id_map = json.load(f)
else:
    id_map = {}

def process_reports(input_folder, output_folder, json_output_file):
    metadata_list = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_folder, filename)
            text = read_pdf_text(file_path)

            # Uncomment the following line to print the OCR text for debugging
            # print(f"\n🧠 OCR TEXT for {filename}:\n{text}\n{'-'*60}")

            # Extract metadata
            metadata = extract_metadata(text)

            # Use the original file identifier (e.g., patient_10785) as real_id
            real_id = filename.replace(".pdf", "")  # patient_10785

            # Get or create anon UUID
            if real_id not in id_map:
                anon_id = str(uuid.uuid4())
                id_map[real_id] = anon_id
            else:
                anon_id = id_map[real_id]

            # Overwrite patient_id in metadata
            metadata["patient_id"] = anon_id
            metadata_list.append(metadata)

            # Save anonymized PDF with UUID filename
            anonymized_text = anonymize_text(text)
            anon_pdf_path = os.path.join(output_folder, f"{anon_id}.pdf")
            write_anonymized_pdf(file_path, anon_pdf_path, anonymized_text)

    # Save updated secure ID map
    with open(ID_MAP_FILE, "w") as f:
        json.dump(id_map, f, indent=4)

    # Save final metadata JSON
    save_metadata_json(metadata_list, json_output_file)
    print(f"\n✅ Metadata JSON saved to: {json_output_file}")
    print(f"✅ Anonymized PDFs saved to: {output_folder}")
    print(f"✅ Secure ID map saved to: {ID_MAP_FILE}")

# Entry point
if __name__ == "__main__":
    raw_dir = "data/raw_reports"
    anon_dir = "data/anonymized_reports"
    json_file = "data/patient_metadata.json"

    os.makedirs(anon_dir, exist_ok=True)
    process_reports(raw_dir, anon_dir, json_file)
