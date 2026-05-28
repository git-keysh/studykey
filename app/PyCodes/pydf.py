import json
import re
from pdf2image import convert_from_path
import pytesseract

# Point to your installations
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'P:\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin'

def extract_questions_with_ocr(pdf_path):
    """Extract question numbers and page numbers using OCR."""
    print(f"Processing {pdf_path}...")
    
    # Convert PDF pages to images
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi=150)
    
    result = []
    
    for page_num, image in enumerate(images, start=1):
        # OCR the page
        text = pytesseract.image_to_string(image)
        
        # Look for question patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Pattern: "1.", "1)", "1.", etc.
            patterns = [
                r'^(\d+)\.',           # 1.
                r'^(\d+)\)',           # 1)
                r'^Item\s+(\d+)',      # Item 1
                r'^(\d+)\s+\.',        # 1 .
            ]
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    q_num = int(match.group(1))
                    if 1 <= q_num <= 60:
                        result.append({"question": q_num, "page": page_num})
                    break
        
        if page_num % 5 == 0:
            print(f"  Processed page {page_num} of {len(images)}")
    
    # Remove duplicates (keep first occurrence of each question)
    seen = set()
    unique = []
    for item in result:
        if item["question"] not in seen:
            seen.add(item["question"])
            unique.append(item)
    
    print(f"  Found {len(unique)} questions")
    return sorted(unique, key=lambda x: x["question"])

# Your PDF files
pdf_files = [
    "CSEC_English_A_P1_2017_MJ.pdf",
    "CSEC_English_A_P1_2018_MJ.pdf",
    "CSEC_English_A_P1_2019_MJ.pdf",
    "CSEC_English_A_P1_2020_MJ.pdf",
    "CSEC_English_A_P1_2021_JAN.pdf",
    "CSEC_English_A_P1_2021_MJ.pdf",
    "CSEC_English_A_P1_2022_MJ.pdf",
    "CSEC_English_A_P1_2023_MJ.pdf",
    "CSEC_English_A_P1_2024_JAN.pdf",
    "CSEC_English_A_P1_2024_MJ.pdf"
]

year_names = {
    "CSEC_English_A_P1_2017_MJ.pdf": "English A MJ 2017",
    "CSEC_English_A_P1_2018_MJ.pdf": "English A MJ 2018",
    "CSEC_English_A_P1_2019_MJ.pdf": "English A MJ 2019",
    "CSEC_English_A_P1_2020_MJ.pdf": "English A MJ 2020",
    "CSEC_English_A_P1_2021_JAN.pdf": "English A Jan 2021",
    "CSEC_English_A_P1_2021_MJ.pdf": "English A MJ 2021",
    "CSEC_English_A_P1_2022_MJ.pdf": "English A MJ 2022",
    "CSEC_English_A_P1_2023_MJ.pdf": "English A MJ 2023",
    "CSEC_English_A_P1_2024_JAN.pdf": "English A Jan 2024",
    "CSEC_English_A_P1_2024_MJ.pdf": "English A MJ 2024"
}

all_data = {}

for pdf_file in pdf_files:
    try:
        questions = extract_questions_with_ocr(pdf_file)
        all_data[year_names[pdf_file]] = questions
    except Exception as e:
        print(f"Error with {pdf_file}: {e}")
        all_data[year_names[pdf_file]] = []

# Save results
with open("all_questions_pages.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print("\nDone! Results saved to all_questions_pages.json")