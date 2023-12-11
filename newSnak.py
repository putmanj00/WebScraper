import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Function to get description from strain-specific page
def get_description(url):
    driver.get(url)
    part_inner_div = driver.find_element(By.CLASS_NAME, 'partInnerDiv')
    paragraphs = part_inner_div.find_elements(By.XPATH, "//p[@class='top05em justi left']")
    description = ' '.join(paragraph.text.strip() for paragraph in paragraphs)
    return description

# URL for the "x" page
url = "https://en.seedfinder.eu/database/strains/alphabetical/x/"

# Lists to store data
strains = []
breeders = []
indica_sativa_list = []
indoor_outdoor_list = []
flowering_time_list = []
female_seeds_list = []
descriptions = []

# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Send an HTTP request to the URL
driver.get(url)

# Find the cannabis strain table
table = driver.find_element(By.ID, "cannabis-strain-table")

# Iterate over each table row
for row in table.find_elements(By.TAG_NAME, "tr")[1:]:
    header = row.find_element(By.CLASS_NAME, "xs1")
    link = header.find_element(By.TAG_NAME, "a")
    strain = link.text.strip()
    breeder = link.get_attribute("title").split("(")[-1].strip(")")

    try:
        indica_sativa_value = row.find_element(By.CSS_SELECTOR, "td img[width='20']").get_attribute("title")
        indoor_outdoor_value = row.find_element(By.CSS_SELECTOR, "td.x20 img[height='14']").get_attribute("title")
        flowering_time_value = row.find_element(By.CSS_SELECTOR, "td.graukleinX span").text
        female_seeds_value = row.find_element(By.CSS_SELECTOR, "td img[width='12']").get_attribute("title")

        strain_url = f"https://en.seedfinder.eu/{link.get_attribute('href')}"
        description = get_description(strain_url)
        descriptions.append(description)

        strains.append(strain)
        breeders.append(breeder)
        indica_sativa_list.append(indica_sativa_value)
        indoor_outdoor_list.append(indoor_outdoor_value)
        flowering_time_list.append(flowering_time_value)
        female_seeds_list.append(female_seeds_value)

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
excel_writer.save()
print("Data saved to cannabis_strains_data.xlsx")

# Quit the WebDriver
driver.quit()
