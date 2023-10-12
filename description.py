import requests
from bs4 import BeautifulSoup
import openpyxl

strain_name = 'X_AE_B-M04'
breeder = 'Humboldt Bred'

def scrape_strain_description(strain_name, breeder):
    # Construct the URL based on strain name and breeder
    url = f"https://en.seedfinder.eu/strain-info/{strain_name.replace(' ', '_')}/{breeder.replace(' ', '_')}/"

    # Fetch the webpage
    strain_page = requests.get(url).text
    strain_soup = BeautifulSoup(strain_page, "html.parser")

    # Find the description
    table = strain_soup.find('div', class_='partInnerDiv')
    strain_description = ""
    if table:
        for p in table.find_all('p'):
            strain_description += p.text.strip() + " "
        strain_description = strain_description.strip()

    return strain_description

print(f'description is: {scrape_strain_description(strain_name, breeder)}')