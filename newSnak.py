import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_description_and_parents(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract description
    part_inner_div = soup.find('div', class_='partInnerDiv')
    paragraphs = part_inner_div.find_all('p', class_='top05em justi left')
    description = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)

    # Extract parent information
    parent1 = None
    parent2 = None

    prnts_div = soup.find('div', {'id': 'prnts'})
    if prnts_div:
        orig_li = prnts_div.find('li', class_='Orig')
        if orig_li:
            strong_tag = orig_li.find('strong')
            if strong_tag:
                parent1 = strong_tag.get_text(strip=True)

            # Extracting parent2
            links = orig_li.find_all('a')
            parent2_parts = []
            for link in links[1:]:
                parent2_parts.append(link.get_text(strip=True))
            parent2 = ' x '.join(parent2_parts)

    return description, parent1, parent2

# Initialize lists to store data
strains = []
breeders = []
indica_sativa = []
indoor_outdoor = []
flowering_time = []
female_seeds = []
descriptions = []
parent1_list = []
parent2_list = []

# strainAlphabeticalList = ["", "1234567890", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
strainAlphabeticalList = ["x"]

# Iterate over each alphabet page
for letter in strainAlphabeticalList:
    url = f'https://en.seedfinder.eu/database/strains/alphabetical/{letter}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the cannabis-strain-table on the page
    table = soup.find('table', class_='SeedTable table-stripeclass:alternate table-autosort')

    # Check if the table is found
    if table:
        # Iterate over each table row
        for row in table.find_all("tr"):
            # Find the table header within the row
            header = row.find("th", {"class": "xs1"})

            # Check if the header is found
            if header:
                link = header.find("a")
                print(f"link header is {link}")
                if link:
                    strain = link.get_text(strip=True)
                    breeder = link["title"].split("(")[-1].strip(")")

                    try:
                        # Extracting description and parent information
                        strain_url = f"https://en.seedfinder.eu/{link['href']}"
                        description, parent1, parent2 = get_description_and_parents(strain_url)

                        # Append strain, breeder, and other information to the lists
                        strains.append(strain)
                        breeders.append(breeder)

                        # Initialize cells as an empty list to avoid NameError
                        cells = []

                        # Find the table data cells for indica/sativa, indoor/outdoor, flowering time, and female seeds
                        if row.find_all("td"):
                            cells = row.find_all("td")

                        indica_sativa.append(cells[2].img["title"] if cells and cells[2].img and "width=\"20\"" in str(cells[2].img) else "")
                        indoor_outdoor.append(cells[3].img["title"] if len(cells) > 3 and cells[3].img and "width=\"13\"" in str(cells[3].img) else "")
                        flowering_time.append(cells[4].span["title"] if len(cells) > 4 and cells[4].span and "class=\"graukleinX\"" in str(cells[4]) else "")
                        female_seeds.append(cells[5].img["title"] if len(cells) > 5 and cells[5].img and "class=\"padL2\"" in str(cells[5].img) else "")
                        descriptions.append(description)
                        parent1_list.append(parent1)
                        parent2_list.append(parent2)

                        # Print information for debugging
                        print(f"Strain: {strain}, Breeder: {breeder}, Description: {description}")
                        print(f"Parent1: {parent1}, Parent2: {parent2}")

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
    'Description': descriptions,
    'Parent1': parent1_list,
    'Parent2': parent2_list
})

# Save the DataFrame to an Excel spreadsheet
excel_writer = pd.ExcelWriter("cannabis_strains_data.xlsx", engine="xlsxwriter")
df.to_excel(excel_writer, sheet_name="Cannabis Strains", index=False)
excel_writer._save()  # Close the ExcelWriter object to save the file
print("Data saved to cannabis_strains_data.xlsx")
