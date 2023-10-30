import aiohttp
import asyncio
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# URL of the website to scrape
url = "https://en.seedfinder.eu/database/strains/alphabetical/"

# Alphabetical list of pages for strains
strainAlphabeticalList = [
    "", "1234567890", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
    "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
]

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

# Function to scrape strain description
async def scrape_strain_description(session, url):
    async with session.get(url, ssl=False) as response:
        try:
            # Use ISO-8859-1 (Latin-1) encoding to handle non-UTF-8 characters
            html = await response.text(encoding='ISO-8859-1')
        except UnicodeDecodeError:
            print(f"Error decoding response at {url}")
            return ""
        return html

# Set up Selenium webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
driver = webdriver.Chrome(options=options)

# Create an asyncio event loop
loop = asyncio.get_event_loop()

async def process_alphabetical_list(url_list):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for x in url_list:
            newUrl = url + x + "/"
            driver.get(newUrl)

            # Wait for the page to load
            time.sleep(5)  # Adjust the wait time as needed

            # Find all rows with strain data
            strain_rows = driver.find_elements(By.CSS_SELECTOR, "table#cannabis-strain-table tbody tr")

            # Inside the loop through each row of strain data
            for row in strain_rows:
                strain = row.find_element(By.CSS_SELECTOR, "th.xs1 a").text
                breeder = row.find_element(By.CSS_SELECTOR, "td.graukleinX.rechts.nowrap").text
                indicaSativa = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
                indoorOutdoor = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
                floweringTime = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
                femaleSeeds = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")
                description_url = f"https://en.seedfinder.eu/strain-info/{strain.replace(' ', '_')}/{breeder.replace(' ', '_')}/"
                tasks.append(scrape_strain_description(session, description_url))

    descriptions = await asyncio.gather(*tasks)

    for row, description in zip(strain_rows, descriptions):
        # Find the first empty row in the Excel sheet
        row_num = sheet.max_row + 1
        
        # Write data to the Excel sheet
        sheet[f"A{row_num}"] = row.find_element(By.CSS_SELECTOR, "th.xs1 a").text
        sheet[f"B{row_num}"] = row.find_element(By.CSS_SELECTOR, "td.graukleinX.rechts.nowrap").text
        sheet[f"C{row_num}"] = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
        sheet[f"D{row_num}"] = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
        sheet[f"E{row_num}"] = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
        sheet[f"F{row_num}"] = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")
        sheet[f"G{row_num}"] = description

# Call the function to process the alphabetical list
loop.run_until_complete(process_alphabetical_list(strainAlphabeticalList))

# Save the Excel workbook
workbook.save("new_strain_data.xlsx")

# Close the browser
driver.quit()

print("Data has been scraped and exported to strain_data.xlsx")
