import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to get description from strain-specific page
def get_description(url):
    # Function to extract description from strain-specific page
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
indica_sativa = []
indoor_outdoor = []
flowering_time = []
female_seeds = []
descriptions = []

# Iterate over each table row
for row in table.find_all("tr"):
    # Find the table header within the row
    header = row.find("th", {"class": "xs1"})

    # Check if the header is found
    if header:
        # Extract the strain and breeder from the href attribute
        link = header.find("a")
        if link:
            strain = link.get_text(strip=True)
            breeder = link["title"].split("(")[-1].strip(")")

            try:
                # Find the table data cells for indica/sativa, indoor/outdoor, flowering time, and female seeds
                cells = row.find_all("td")

                # Extract indica/sativa information
                indica_sativa.append(cells[2].img["title"] if cells and cells[2].img and "width=\"20\"" in str(cells[2].img) else "")

                # Extract indoor/outdoor information
                indoor_outdoor.append(cells[3].img["title"] if len(cells) > 3 and cells[3].img and "width=\"13\"" in str(cells[3].img) else "")

                # Extract flowering time information
                flowering_time.append(cells[4].span["title"].replace("Flowering time in days: ", "") if len(cells) > 4 and cells[4].span and "class=\"graukleinX\"" in str(cells[4]) else "")

                # Extract female seeds information
                female_seeds.append(cells[5].img["title"] if len(cells) > 5 and cells[5].img and "class=\"padL2\"" in str(cells[5].img) else "")

                # Extract strain-specific page URL and get description
                strain_url = f"https://en.seedfinder.eu/{link['href']}"
                description = get_description(strain_url)
                descriptions.append(description)

                # Append strain and breeder to the lists
                strains.append(strain)
                breeders.append(breeder)

            except Exception as e:
                print(f"Failed to process data for strain '{strain}'. Error: {e}")

# Create a DataFrame from the lists
df = pd.DataFrame({
    'Strain': strains,
    'Breeder': breeders,
    'Indica or Sativa': indica_sativa,
    'Indoor or Outdoor': indoor_outdoor,
    'Flowering Time(Days)': flowering_time,
    'Female Seeds(?)': female_seeds,
    'Description': descriptions
})

# Save the DataFrame to an Excel spreadsheet
excel_writer = pd.ExcelWriter("cannabis_strains_data.xlsx", engine="xlsxwriter")
df.to_excel(excel_writer, sheet_name="Cannabis Strains", index=False)
excel_writer.save()  # Save the ExcelWriter object to save the file
print("Data saved to cannabis_strains_data.xlsx")
