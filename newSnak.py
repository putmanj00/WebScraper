import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to extract description from strain-specific page
def get_description(strain_url):
    try:
        response = requests.get(strain_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the strain-specific page for {strain_url}. Error: {e}")
        return ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        part_inner_div = soup.find("div", class_="partInnerDiv")
        if part_inner_div:
            paragraphs = part_inner_div.find_all("p", class_=lambda x: x and "top05em" in x)
            description = " ".join([p.get_text(strip=True) for p in paragraphs])
            return description
        else:
            print(f"Failed to find 'partInnerDiv' class for {strain_url}.")
    else:
        print(f"Failed to fetch the strain-specific page for {strain_url}. Status code: {response.status_code}")

    return ""

# Define the URL for the "a" page
url = "https://en.seedfinder.eu/database/strains/alphabetical/x"

# Send a GET request to the URL
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch the page. Error: {e}")
    exit()

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with the specified ID
    table = soup.find("table", {"id": "cannabis-strain-table"})

    # Check if the table is found
    if table:
        # Initialize lists to store strain, breeder, indica/sativa, indoor/outdoor, flowering time, female seeds, and description information
        strains = []
        breeders = []
        indica_sativa = []
        indoor_outdoor = []
        flowering_time = []
        female_seeds = []
        descriptions = []  # New list for description information

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
                        indica_sativa.append(cells[0].img["title"] if cells and cells[0].img else "")

                        # Extract indoor/outdoor information
                        indoor_outdoor.append(cells[1].img["title"] if len(cells) > 1 and cells[1].img else "")

                        # Extract flowering time information
                        flowering_time.append(cells[2].span["title"] if len(cells) > 2 and cells[2].span else "")

                        # Extract female seeds information
                        female_seeds.append(cells[3].img["title"] if len(cells) > 3 and cells[3].img else "")

                        # Extract strain-specific page URL and get description
                        strain_url = f"https://en.seedfinder.eu/{link['href']}"
                        description = get_description(strain_url)
                        descriptions.append(description)

                        # Append strain and breeder to the lists
                        strains.append(strain)
                        breeders.append(breeder)

                    except Exception as e:
                        print(f"Failed to process data for strain '{strain}'. Error: {e}")

        # Now, you have lists with all the information
        # Create a DataFrame using pandas
        data = {
            "Strain": strains,
            "Breeder": breeders,
            "Indica or Sativa": indica_sativa,
            "Indoor or Outdoor": indoor_outdoor,
            "Flowering Time(Days)": flowering_time,
            "Female Seeds(?)": female_seeds,
            "Description": descriptions,  # Add the new column
        }

        df = pd.DataFrame(data)

        # Save the DataFrame to an Excel spreadsheet
        excel_writer = pd.ExcelWriter("cannabis_strains_data.xlsx", engine="xlsxwriter")
        df.to_excel(excel_writer, sheet_name="Cannabis Strains", index=False)
        excel_writer.save()

        print("Data saved to cannabis_strains_data.xlsx")

    else:
        print("Table not found on the page.")
else:
    print(f"Failed to fetch the page {url}. Status code: {response.status_code}")
