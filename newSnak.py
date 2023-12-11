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
                # Extracting information for Indica or Sativa
                indica_sativa = row.find("td", {"class": "xs1"}).img["title"] if row.find("td", {"class": "xs1"}) else ""

                # Extracting information for Indoor or Outdoor
                indoor_outdoor = row.find("td", {"class": "x20"}).img["title"] if row.find("td", {"class": "x20"}) else ""

                # Extracting information for Flowering Time(Days)
                flowering_time = row.find("td", {"class": "graukleinX"}).span.text if row.find("td", {"class": "graukleinX"}) else ""

                # Extracting information for Female Seeds(?)
                female_seeds = row.find("td", {"class": "padL2"}).img["title"] if row.find("td", {"class": "padL2"}) else ""

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
