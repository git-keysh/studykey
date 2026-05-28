import requests
import os
from urllib.parse import urlparse

# List of URLs
urls = [
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2025_MJ.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2024_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2024_MJ.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2023_MJ.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2023_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2022_MJ.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2021_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2020_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2019_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2019_MJ.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2018_JAN.pdf",
    "https://api.caribbeans.ai/past_papers/csec/Mathematics/Paper%201/CSEC_Mathematics_P1_2017_MJ.pdf"
]

# Create download directory if it doesn't exist
download_dir = "csec_mathematics_papers"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

def download_pdf(url, save_dir):
    """Download a PDF from URL and save it with filename derived from URL"""
    try:
        # Extract filename from URL (last part after /)
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Decode %20 to spaces (though spaces in filenames are fine)
        filename = filename.replace('%20', '_')
        
        # Full path to save the file
        filepath = os.path.join(save_dir, filename)
        
        print(f"Downloading: {filename}")
        
        # Send HTTP request
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for download errors
        
        # Save file
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"✓ Successfully saved: {filepath}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error with {url}: {e}")
        return False

# Download all files
print("Starting download of CSEC Mathematics Paper 1 past papers...")
print(f"Files will be saved to: {os.path.abspath(download_dir)}/\n")

successful = 0
failed = 0

for url in urls:
    if download_pdf(url, download_dir):
        successful += 1
    else:
        failed += 1
    print()  # Add blank line for readability

# Summary
print("=" * 50)
print(f"Download complete!")
print(f"✓ Successful: {successful}")
print(f"✗ Failed: {failed}")
print(f"Files saved in: {os.path.abspath(download_dir)}/")