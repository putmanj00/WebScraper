import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Function to get description from strain-specific page
def get_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    part_inner_div = soup.find('div', class_='partInnerDiv')
    paragraphs = part_inner_div.find_all('p', class_='top05em justi left')
    description = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    return description

# Download the latest Chromedriver version
os.system("wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE -O chromedriver_version.txt")
with open("chromedriver_version.txt", "r") as file:
    chromedriver_version = file.read().strip()

# Download Chromedriver
chromedriver_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
os.system(f"wget {chromedriver_url} && unzip chromedriver_linux64.zip")

# Set the path to Chromedriver
chromedriver_path = os.path.abspath("chromedriver")

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode

# Create a Chrome webdriver with the specified options
try:
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    print("Chromedriver successfully initiated.")
except Exception as e:
    print(f"Error initiating Chromedriver: {e}")
    exit(1)

# URL for the "x" page
url = "https://en.seedfinder.eu/database/strains/alphabetical/x/"