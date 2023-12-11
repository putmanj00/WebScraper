import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By  # Import the By class

# Function to get description from strain-specific page
def get_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    part_inner_div = soup.find('div', class_='partInnerDiv')
    paragraphs = part_inner_div.find_all('p', class_='top05em justi left')
    description = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    return description

# URL for the "x" page
url = "https://en.seedfinder.eu/database/strains/alphabetical/x/"

# Set up the Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Send an HTTP request to the URL
driver.get(url)

# Find the cannabis strain table
table = driver.find_element(By.ID, "cannabis-strain-table")

# Lists to store data
strains = []
breeders = []
indica_sativa_list = []
indoor_outdoor_list = []
flowering_time_list = []
female_seeds_list = []
descriptions = []

# Iterate over each table row
for row in table.find_elements(By.TAG_NAME, "tr"):
    header = row.find_element(By.CLASS_NAME, "xs1")
    if header:
        link = header.find_element(By.TAG_NAME, "a")
        if link:
            strain = link.text.strip()
            breeder = link.get_attribute("title").split("(")[-1].strip(")")

            try:
                # Extracting information for Indica or Sativa
                indica_sativa = row.find_element(By.CSS_SELECTOR, "td.greenC[width='20'] img").get_attribute("title") if row.find_element(By.CSS_SELECTOR, "td.greenC[width='20'] img") else ""

                # Extracting information for Indoor or Outdoor
                indoor_outdoor = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title") if row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']") else ""

                # Extracting information for Flowering Time(Days)
                flowering_time = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text if row.find_element(By.CSS_SELECTOR, "td.graukleinX span") else ""

                # Extracting information for Female Seeds(?)
                female_seeds = row.find_element(By.CSS_SELECTOR, "td.padL2[width='12'] img").get_attribute("title") if row.find_element(By.CSS_SELECTOR, "td.padL2[width='12'] img") else ""

                strain_url = f"https://en.seedfinder.eu/{link.get_attribute('href')}"
                description = get_description(strain_url)
                descriptions.append(description)

                strains.append(strain)
                breeders.append(breeder)
                indica_sativa_list.append(indica_sativa)
                indoor_outdoor_list.append(indoor_outdoor)
                flowering_time_list.append(flowering_time)
                female_seeds_list.append(female_seeds)

            except Exception as e:
                print(f"Failed to process data for strain '{strain}'. Error: {e}")

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
excel_writer._save()
print("Data saved to cannabis_strains_data.xlsx")

# Close the WebDriver
driver.quit()
