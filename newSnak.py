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


# Send an HTTP request to the URL
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.content, "html.parser")

# Find the cannabis strain table
table = soup.find("table", {"id": "cannabis-strain-table"})

# Lists to store data
strains = []
breeders = []
indica_sativa_list = []
indoor_outdoor_list = []
flowering_time_list = []
female_seeds_list = []
descriptions = []

# Iterate over each table row
for row in table.find_all("tr"):
    header = row.find("th", {"class": "xs1"})
    if header:
        link = header.find("a")
        if link:
            strain = link.get_text(strip=True)
            breeder = link["title"].split("(")[-1].strip(")")

            try:
                indica_sativa = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
                indoor_outdoor = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
                flowering_time = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
                female_seeds = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")

                strain_url = f"https://en.seedfinder.eu/{link['href']}"
                description = get_description(strain_url)
                descriptions.append(description)

                strains.append(strain)
                breeders.append(breeder)
                indica_sativa_list.append(indica_sativa)
                indoor_outdoor_list.append(indoor_outdoor)
                flowering_time_list.append(flowering_time)
                female_seeds_list.append(female_seeds)

            except AttributeError as e:
                print(f"Failed to process data for strain '{strain}'. Error: {e}")
                continue

# Create a DataFrame from the lists
df = pd.DataFrame({
    'Strain': strains,
    'Breeder': breeders,
    'Indica or Sativa': indica_sativa_list,
    'Indoor or Outdoor': indoor_outdoor_list,
    'Flowering Time(Days)': flowering_time_list,
    'Female Seeds(?)': female_seeds_list,
    'Description': descriptions
})

# Save the DataFrame to an Excel spreadsheet
excel_writer = pd.ExcelWriter("cannabis_strains_data.xlsx", engine="xlsxwriter")
df.to_excel(excel_writer, sheet_name="Cannabis Strains", index=False)
excel_writer.save()
print("Data saved to cannabis_strains_data.xlsx")
