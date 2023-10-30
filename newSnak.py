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
# strainAlphabeticalList = ["", "1234567890", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
strainAlphabeticalList = [""]

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

def escape_xlsx_char(ch):
	illegal_xlsx_chars = {
	'\x00':'\\x00',	#	NULL
	'\x01':'\\x01',	#	SOH
	'\x02':'\\x02',	#	STX
	'\x03':'\\x03',	#	ETX
	'\x04':'\\x04',	#	EOT
	'\x05':'\\x05',	#	ENQ
	'\x06':'\\x06',	#	ACK
	'\x07':'\\x07',	#	BELL
	'\x08':'\\x08',	#	BS
	'\x0b':'\\x0b',	#	VT
	'\x0c':'\\x0c',	#	FF
	'\x0e':'\\x0e',	#	SO
	'\x0f':'\\x0f',	#	SI
	'\x10':'\\x10',	#	DLE
	'\x11':'\\x11',	#	DC1
	'\x12':'\\x12',	#	DC2
	'\x13':'\\x13',	#	DC3
	'\x14':'\\x14',	#	DC4
	'\x15':'\\x15',	#	NAK
	'\x16':'\\x16',	#	SYN
	'\x17':'\\x17',	#	ETB
	'\x18':'\\x18',	#	CAN
	'\x19':'\\x19',	#	EM
	'\x1a':'\\x1a',	#	SUB
	'\x1b':'\\x1b',	#	ESC
	'\x1c':'\\x1c',	#	FS
	'\x1d':'\\x1d',	#	GS
	'\x1e':'\\x1e',	#	RS
	'\x1f':'\\x1f'}	#	US
	
	if ch in illegal_xlsx_chars:
		return illegal_xlsx_chars[ch]
	
	return ch
	
#
# Wraps the function escape_xlsx_char(ch).
def escape_xlsx_string(st):
	
	return ''.join([escape_xlsx_char(ch) for ch in st])

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
            strain_description = strain_description.replace("±", "+/-")
            # strain_description = re.sub(r'[^\x00-\x7F]+', '', strain_description)

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
        sheet[f"A{row_num}"] = escape_xlsx_char(strain)
        sheet[f"B{row_num}"] = escape_xlsx_char(breeder)
        sheet[f"C{row_num}"] = escape_xlsx_char(indicaSativa)
        sheet[f"D{row_num}"] = escape_xlsx_char(indoorOutdoor)
        sheet[f"E{row_num}"] = escape_xlsx_char(floweringTime)
        sheet[f"F{row_num}"] = escape_xlsx_char(femaleSeeds)
        sheet[f"G{row_num}"] = escape_xlsx_char(description)

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
