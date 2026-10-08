import easyocr
import re

def extract_aadhaar_details(image_path):
    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)
    
    # Read the text from the image
    results = reader.readtext(image_path, detail=0)
    full_text = "\n".join(results)

    # Initialize variables
    aadhaar_number = None
    dob = None
    name = None
    gender = None

    # Aadhaar Number Pattern (4-4-4 digits)
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', full_text)
    if aadhaar_match:
        aadhaar_number = aadhaar_match.group()

    # Improved patterns that account for OCR inconsistencies
    # Name pattern (looks for "Name" followed by punctuation and spaces)
    name_match = re.search(r'(?:Name|NAME)\s*[:]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', full_text, re.IGNORECASE)
    if not name_match:
        # Alternative pattern if the above fails
        name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?=\s*(?:DOB|Gender|Aadhaar))', full_text)
    if name_match:
        name = name_match.group(1).strip()

    # DOB pattern (more flexible with spacing/format)
    dob_match = re.search(r'(?:DOB|Date of Birth)\s*[:]?\s*(\d{2}/\d{2}/\d{4})', full_text, re.IGNORECASE)
    if dob_match:
        dob = dob_match.group(1)
    else:
        # Fallback to finding any date in the correct format
        dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', full_text)
        if dob_match:
            dob = dob_match.group()

    # Gender pattern
    gender_match = re.search(r'(?:Gender|SEX)\s*[:]?\s*([MF]ale|Female|M|F)', full_text, re.IGNORECASE)
    if gender_match:
        gender = gender_match.group(1)
        # Standardize gender format
        if gender.upper().startswith('M'):
            gender = "Male"
        elif gender.upper().startswith('F'):
            gender = "Female"

    print("\n📄 Aadhaar Details Extracted:")
    print(f" Name         : {name if name else 'Not found'}")
    print(f" Gender       : {gender if gender else 'Not found'}")
    print(f" Aadhaar No.  : {aadhaar_number if aadhaar_number else 'Not found'}")
    print(f" DOB          : {dob if dob else 'Not found'}")

if __name__ == "__main__":

    filepath = "/Users/abhinavk/CochinComputing2/output/aadhaar/aadhaar_11.jpg"
    extract_aadhaar_details(filepath)