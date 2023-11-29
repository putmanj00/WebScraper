import string
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
import openpyxl
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import re

# URL of the website to scrape
url = "https://en.seedfinder.eu/database/strains/alphabetical/"

# Alphabetical list of pages for strains
strainAlphabeticalList = ["v"]

# Create a new Excel workbook
workbook = openpyxl.Workbook()
sheet = workbook.active

# Write headers to the Excel sheet
sheet["A1"] = "Strain"
sheet["B1"] = "Breeder"
sheet["C1"] = "Indica or Sativa"
sheet["D1"] = "Indoor or Outdoor"
sheet["E1"] = "Flowering Time (Days)"
sheet["F1"] = "Female Seeds?"
sheet["G1"] = "Description"

def sanitize_string(input_str):
    # Remove newline characters and other non-printable characters
    sanitized_str = ''.join(char for char in input_str if char in string.printable)
    return sanitized_str

def clean_for_excel(value):
    # Replace non-printable ASCII characters with a space
    cleaned_value = re.sub(r'[^\x20-\x7E]', ' ', value)
    return cleaned_value

async def scrape_strain_description(session, strain_name, breeder):
    url = f"https://en.seedfinder.eu/strain-info/{strain_name.replace(' ', '_')}/{breeder.replace(' ', '_')}/"

    async with session.get(url, ssl=False) as response:
        try:
            html = await response.text(encoding='UTF-8')
        except UnicodeDecodeError:
            print(f"Error decoding response at {url}")
            return ""
    
        strain_soup = BeautifulSoup(html, "html.parser")

        table = strain_soup.find('div', class_='partInnerDiv')
        strain_description = ""
        if table:
            for p in table.find_all('p'):
                strain_description += p.text.strip().replace("\n", "")
            strain_description = strain_description.strip()

        return sanitize_string(strain_description)

async def process_alphabetical_list(session, driver, x):
    newUrl = url + x + "/"
    driver.get(newUrl)

    time.sleep(5)  # Adjust the wait time as needed

    strain_rows = driver.find_elements(By.CSS_SELECTOR, "table#cannabis-strain-table tbody tr")

    tasks = []

    print(f"Scraping data for page '{x}'...")

    for row in strain_rows:
        strain = row.find_element(By.CSS_SELECTOR, "th.xs1 a").text
        breeder = row.find_element(By.CSS_SELECTOR, "td.graukleinX.rechts.nowrap").text
        indicaSativa = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
        indoorOutdoor = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
        floweringTime = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
        femaleSeeds = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")
        
        tasks.append(scrape_strain_description(session, strain, breeder))

    descriptions = await asyncio.gather(*tasks)

    print(f"Data scraped for page '{x}'. Writing to Excel...")

    for i, description in enumerate(descriptions):
        row = strain_rows[i]
        strain = row.find_element(By.CSS_SELECTOR, "th.xs1 a").text
        breeder = row.find_element(By.CSS_SELECTOR, "td.graukleinX.rechts.nowrap").text
        indicaSativa = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
        indoorOutdoor = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
        floweringTime = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
        femaleSeeds = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")

        # Find the first empty row in the Excel sheet
        row_num = sheet.max_row + 1

        # Write data to the Excel sheet
        sheet[f"A{row_num}"] = clean_for_excel(strain)
        sheet[f"B{row_num}"] = clean_for_excel(breeder)
        sheet[f"C{row_num}"] = clean_for_excel(indicaSativa)
        sheet[f"D{row_num}"] = clean_for_excel(indoorOutdoor)
        sheet[f"E{row_num}"] = clean_for_excel(floweringTime)
        sheet[f"F{row_num}"] = clean_for_excel(femaleSeeds)
        sheet[f"G{row_num}"] = clean_for_excel(description)

    print(f"Data written to Excel for page '{x}'.")

async def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    async with ClientSession() as session:
        tasks = [process_alphabetical_list(session, driver, x) for x in strainAlphabeticalList]
        await asyncio.gather(*tasks)

    driver.quit()

    # Save the Excel workbook
    workbook.save("new_strain_data.xlsx")

    print("Data has been scraped and exported to strain_data.xlsx")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
