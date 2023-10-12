# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# geneticsUrl = "https://en.seedfinder.eu/database/strains/alphabetical/"
# strainUrl = "https://en.seedfinder.eu/strain-info/A_Cheesy_Mist/Kalis_Fruitful_Cannabis_Seeds/"
# strainAlphabeticalList = [""]
# # strainAlphabeticalList = ["", "1234567890", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# dfs = []

# for x in strainAlphabeticalList:
#     newGeneticsUrl = geneticsUrl + x + "/"
#     page = requests.get(newGeneticsUrl).text
#     soup = BeautifulSoup(page, "html.parser")
#     table = soup.find('table', class_='SeedTable table-stripeclass:alternate table-autosort')

#     data = []
#     for row in table.tbody.find_all('tr'):
#         # Strain column
#         strain_column = row.find_all('th', class_='xs1')
#         #breeder column
#         breeder_column = row.find_all('td', class_='graukleinX rechts nowrap')
#         #indica or sativa column
#         indica_sativa_column = ""
#         for img in row.find_all(attrs={"width" : "20"}):
#             indica_sativa_column = img["title"]
#         #indoor or outdoor column
#         indoor_outdoor_column = ""
#         for img in row.find_all(attrs={"width" : "13"}):
#             indoor_outdoor_column = img["title"]
#         #flowering times column
#         flowering_time_column = row.find_all("span", title=True)
#         #female seed column
#         female_seeds_column = ""
#         for img in row.find_all(attrs={"width" : "12"}):
#             female_seeds_column = img["title"]
#         # Strain URL column
#         strain_url_column = ""
#         strain_description_column = ""
#         th_classes = row.find('th', {'class': 'xs1'})
#         children = th_classes.findChildren('a', recursive=False)
#         for child in children:
#             strain_url_column = child['href'].replace("../../../../", "https://en.seedfinder.eu/")
#             strain_page = requests.get(strain_url_column).text
#             strain_soup = BeautifulSoup(strain_page, "html.parser")
#             table = strain_soup.find('div', class_='partInnerDiv')
#             strain_description = ""
#             for p in table.find_all('p'):
#                 strain_description += p.text.strip() + " "
#                 strain_description_column = strain_description.strip()

#         row_data = {}

#         if strain_column:
#             cannabis_strain = strain_column[0].text.strip()
#             row_data['Cannabis Strain'] = cannabis_strain

#         if breeder_column:
#             breeder = breeder_column[0].text.strip()
#             row_data['Breeder'] = breeder

#         if indica_sativa_column:
#             indica_sativa = indica_sativa_column
#             row_data['Indica or Sativa'] = indica_sativa

#         if indoor_outdoor_column:
#             indoor_outdoor = indoor_outdoor_column
#             row_data['Indoor/Outdoor'] = indoor_outdoor

#         if flowering_time_column:
#             flowering_time = flowering_time_column[0].text.strip()
#             row_data['Flowering Time'] = flowering_time

#         if female_seeds_column:
#             female_seeds = female_seeds_column
#             row_data['Female Seeds'] = female_seeds

#         if strain_url_column:
#             strain_url = strain_url_column
#             row_data['Strain URL'] = strain_url
        
#         if strain_description_column:
#             strain_description = strain_description_column
#             row_data['Strain Description'] = strain_description

#     df = pd.DataFrame(data)
#     dfs.append(df)

# df = pd.concat(dfs, ignore_index=True)
# df = df.dropna()
# df.reset_index(drop=True, inplace=True)
# print(df.head(10))

# # df.to_excel("output.xlsx", index=False)


import requests
from bs4 import BeautifulSoup
import pandas as pd

geneticsUrl = "https://en.seedfinder.eu/database/strains/alphabetical/"
strainUrl = "https://en.seedfinder.eu/strain-info/A_Cheesy_Mist/Kalis_Fruitful_Cannabis_Seeds/"
strainAlphabeticalList = [""]
dfs = []

for x in strainAlphabeticalList:
    newGeneticsUrl = geneticsUrl + x + "/"
    page = requests.get(newGeneticsUrl).text
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find('table', class_='SeedTable table-stripeclass:alternate table-autosort')

    data = []
    for row in table.tbody.find_all('tr'):
        # Strain column
        strain_column = row.find_all('th', class_='xs1')
        #breeder column
        breeder_column = row.find_all('td', class_='graukleinX rechts nowrap')
        #indica or sativa column
        indica_sativa_column = ""
        for img in row.find_all(attrs={"width" : "20"}):
            indica_sativa_column = img["title"]
        #indoor or outdoor column
        indoor_outdoor_column = ""
        for img in row.find_all(attrs={"width" : "13"}):
            indoor_outdoor_column = img["title"]
        #flowering times column
        flowering_time_column = row.find_all("span", title=True)
        #female seed column
        female_seeds_column = ""
        for img in row.find_all(attrs={"width" : "12"}):
            female_seeds_column = img["title"]
        # Strain URL column
        strain_url_column = ""
        strain_description_column = ""
        th_classes = row.find('th', {'class': 'xs1'})
        children = th_classes.findChildren('a', recursive=False)
        for child in children:
            strain_url_column = child['href'].replace("../../../../", "https://en.seedfinder.eu/")
            strain_page = requests.get("https://en.seedfinder.eu/strain-info/XL_Italian_Shoes/Cult_Classics_Seeds/").text
            strain_soup = BeautifulSoup(strain_page, "html.parser")
            table = strain_soup.find('div', class_='partInnerDiv')
            strain_description = ""
            if table:
                for p in table.find_all('p'):
                    strain_description += p.text.strip() + " "
                strain_description_column = strain_description.strip()

        row_data = {}
        
        if strain_description_column:
            strain_description = strain_description_column
            row_data['Strain Description'] = strain_description


df = pd.concat(dfs, ignore_index=True)
df = df.dropna()
df.reset_index(drop=True, inplace=True)
print(df.head(10))

# df.to_excel("output.xlsx", index=False)
# print(df.head(10).loc[:, ~data.columns.isin(['Breeder', 'Indicia or Sativa', 'Indoor/Outdoor'])])