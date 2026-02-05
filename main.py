import os
import sys
import pytesseract
import uuid
import json
import traceback
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
    """Process all PDF reports with per-file error handling."""
    metadata_list = []
    results = {'success': 0, 'errors': 0, 'failed_files': []}

    # Validate input folder
    input_path = Path(input_folder)
    if not input_path.exists():
        raise ValueError(f"Input directory not found: {input_folder}")
    
    # Get PDF files
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith(".pdf")]
    if not pdf_files:
        raise ValueError(f"No PDF files found in {input_folder}")
    
    print(f"\n📋 Processing {len(pdf_files)} PDF files...\n")

    for filename in pdf_files:
        file_path = os.path.join(input_folder, filename)
        
        try:
            # Extract text with OCR
            try:
                text = read_pdf_text(file_path)
            except Exception as e:
                raise ValueError(f"OCR failed: {e}")

            # Uncomment the following line to print the OCR text for debugging
            # print(f"\n🧠 OCR TEXT for {filename}:\n{text}\n{'-'*60}")

            # Extract metadata
            try:
                metadata = extract_metadata(text)
            except Exception as e:
                raise ValueError(f"Metadata extraction failed: {e}")

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
            try:
                anonymized_text = anonymize_text(text)
                anon_pdf_path = os.path.join(output_folder, f"{anon_id}.pdf")
                write_anonymized_pdf(file_path, anon_pdf_path, anonymized_text)
            except Exception as e:
                raise ValueError(f"PDF generation failed: {e}")
            
            results['success'] += 1
            print(f"✅ {filename} → {anon_id}.pdf")
        
        except Exception as e:
            results['errors'] += 1
            results['failed_files'].append(filename)
            print(f"❌ Error processing {filename}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            continue  # Continue with next file

    # Save updated secure ID map
    try:
        with open(ID_MAP_FILE, "w") as f:
            json.dump(id_map, f, indent=4)
    except Exception as e:
        print(f"⚠️  Warning: Could not save ID map: {e}", file=sys.stderr)

    # Save final metadata JSON (only successful extractions)
    if metadata_list:
        try:
            save_metadata_json(metadata_list, json_output_file)
            print(f"\n✅ Metadata JSON saved to: {json_output_file}")
        except Exception as e:
            print(f"❌ Error saving metadata JSON: {e}", file=sys.stderr)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully processed: {results['success']} files")
    print(f"❌ Failed: {results['errors']} files")
    if results['failed_files']:
        print(f"\nFailed files:")
        for fname in results['failed_files']:
            print(f"  - {fname}")
    print(f"{'='*60}\n")
    
    return results

# Entry point
if __name__ == "__main__":
    try:
        raw_dir = "data/raw_reports"
        anon_dir = "data/anonymized_reports"
        json_file = "data/patient_metadata.json"

        os.makedirs(anon_dir, exist_ok=True)
        results = process_reports(raw_dir, anon_dir, json_file)
        
        # Exit with error code if any files failed
        if results['errors'] > 0:
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
