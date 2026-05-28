import pdf2image
import pytesseract
import numpy as np
import cv2
import re
import yaml
from PIL import Image
from typing import List, Dict, Optional

def deskew_image(image):
    """Deskew an image by detecting text rotation angle."""
    # Convert to grayscale and invert
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray = cv2.bitwise_not(gray)
    
    # Threshold
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Find all coordinates of non-zero pixels
    coords = np.column_stack(np.where(thresh > 0))
    
    if len(coords) < 10:
        return image  # Skip if not enough text
    
    # Get min area rectangle angle
    angle = cv2.minAreaRect(coords)[-1]
    
    # Adjust angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Rotate if angle is significant
    if abs(angle) > 0.5:
        (h, w) = image.height, image.width
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(np.array(image), M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        return Image.fromarray(rotated)
    return image

def extract_questions_from_text(text: str) -> List[Dict]:
    """Parse OCR text into structured questions with options."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    questions = []
    current_q = None
    option_pattern = r'^([A-D])\.\s+(.+)$'
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Match question number pattern (1., 2., etc.)
        q_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if q_match:
            # Save previous question
            if current_q and 'text' in current_q:
                questions.append(current_q)
            
            # Start new question
            q_num = int(q_match.group(1))
            q_text = q_match.group(2)
            current_q = {
                'number': q_num,
                'question': q_text,
                'options': {},
                'correct_answer': None
            }
            i += 1
            continue
        
        # Match options (A. xxx, B. xxx, etc.)
        opt_match = re.match(option_pattern, line)
        if opt_match and current_q:
            letter = opt_match.group(1)
            opt_text = opt_match.group(2).strip()
            current_q['options'][letter] = opt_text
            i += 1
            continue
        
        # Check for "Answer: X" or "correct_answer: X" patterns
        ans_match = re.search(r'(?:answer|correct)[\s:]+([A-D])', line, re.IGNORECASE)
        if ans_match and current_q:
            current_q['correct_answer'] = ans_match.group(1)
            i += 1
            continue
        
        # If line doesn't match anything but we have a current question,
        # it might be a continuation of the question text
        if current_q and not re.match(option_pattern, line) and not re.match(r'^\d+\.', line):
            current_q['question'] += ' ' + line
            i += 1
            continue
        
        i += 1
    
    # Add last question
    if current_q and 'text' in current_q:
        questions.append(current_q)
    
    # Filter out incomplete questions
    questions = [q for q in questions if len(q['options']) == 4]
    
    return questions

def detect_answers_from_multiple_pages(pages_text: List[str]) -> Dict[int, str]:
    """Attempt to find answer keys from all pages (e.g., '1. A', '2. C')."""
    answers = {}
    answer_pattern = re.compile(r'^(\d+)\.\s*([A-D])', re.IGNORECASE)
    
    for text in pages_text:
        for line in text.split('\n'):
            match = answer_pattern.match(line.strip())
            if match:
                q_num = int(match.group(1))
                ans = match.group(2).upper()
                answers[q_num] = ans
    
    return answers

def main(pdf_path: str, output_yaml: str = "csec_math_2025.yaml"):
    print(f"Processing PDF: {pdf_path}")
    
    # Convert PDF pages to images
    print("Converting PDF to images...")
    images = pdf2image.convert_from_path(pdf_path, dpi=300)
    
    all_text = []
    all_questions = []
    answer_key = {}
    
    for idx, img in enumerate(images):
        print(f"Processing page {idx + 1}/{len(images)}...")
        
        # Deskew the image
        deskewed = deskew_image(img)
        
        # OCR with English language
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(deskewed, config=custom_config)
        all_text.append(text)
        
        # Extract questions from this page
        page_questions = extract_questions_from_text(text)
        
        # Merge with existing questions (avoid duplicates by number)
        existing_nums = {q['number'] for q in all_questions}
        for q in page_questions:
            if q['number'] not in existing_nums:
                all_questions.append(q)
    
    # Sort questions by number
    all_questions.sort(key=lambda x: x['number'])
    
    # Try to detect answer key from all pages
    answer_key = detect_answers_from_multiple_pages(all_text)
    
    # Assign correct answers if found
    for q in all_questions:
        if q['number'] in answer_key:
            q['correct_answer'] = answer_key[q['number']]
        elif not q['correct_answer']:
            q['correct_answer'] = "Not found"
    
    # Prepare YAML structure
    exam_data = {
        'exam': {
            'title': 'CSEC Mathematics P1 2025 MJ',
            'year': 2025,
            'subject': 'Mathematics',
            'total_items': len(all_questions),
            'items': all_questions
        }
    }
    
    # Write YAML file
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(exam_data, f, allow_unicode=True, sort_keys=False, indent=2)
    
    print(f"\n✅ YAML saved to: {output_yaml}")
    print(f"📊 Total questions extracted: {len(all_questions)}")
    
    # Show sample
    if all_questions:
        print("\n📝 Sample question:")
        sample = all_questions[0]
        print(f"  {sample['number']}. {sample['question']}")
        for opt, text in sample['options'].items():
            print(f"     {opt}. {text}")
        print(f"  ✅ Correct: {sample['correct_answer']}")

if __name__ == "__main__":
    # Install required packages first:
    # pip install pdf2image pytesseract opencv-python pillow pyyaml numpy
    
    # Also need Tesseract installed on your system:
    # Windows: https://github.com/UB-Mannheim/tesseract/wiki
    # Mac: brew install tesseract
    # Linux: sudo apt install tesseract-ocr
    
    import sys
    if len(sys.argv) < 2:
        print("Usage: python deskew_ocr_yaml.py <pdf_file> [output_yaml]")
        print("Example: python deskew_ocr_yaml.py CSEC_Mathematics_P1_2025_MJ.pdf math_2025.yaml")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "csec_math_2025.yaml"
    
    main(pdf_file, out_file)