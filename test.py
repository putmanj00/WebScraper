import requests
from bs4 import BeautifulSoup
import pandas as pd

geneticsUrl = "https://en.seedfinder.eu/database/strains/alphabetical/"
strainUrl = "https://en.seedfinder.eu/strain-info/A_Cheesy_Mist/Kalis_Fruitful_Cannabis_Seeds/"
strainAlphabeticalList = ["x"]
# strainAlphabeticalList = ["", "1234567890", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
dfs = []
dfs2 = []

def extract_text(string):
    # Extract text to the right of the last "»" character
    last_arrow_index = string.rfind("»")
    right_of_arrow = string[last_arrow_index + 1:].strip()
    left_of_arrow = string[:last_arrow_index].strip(" »»")

    return right_of_arrow, left_of_arrow

for x in strainAlphabeticalList:
    newGeneticsUrl = geneticsUrl + x + "/"
    page = requests.get(newGeneticsUrl).text
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find('table', class_='SeedTable table-stripeclass:alternate table-autosort')

    parents_list = []
    data = []
    for row in table.tbody.find_all('tr'):
        # # Strain column
        # strain_column = row.find_all('th', class_='xs1')
        # #breeder column
        # breeder_column = row.find_all('td', class_='graukleinX rechts nowrap')
        # #indica or sativa column
        # indica_sativa_column = ""
        # for img in row.find_all(attrs={"width" : "20"}):
        #     indica_sativa_column = img["title"]
        # #indoor or outdoor column
        # indoor_outdoor_column = ""
        # for img in row.find_all(attrs={"width" : "13"}):
        #     indoor_outdoor_column = img["title"]
        # #flowering times column
        # flowering_time_column = row.find_all("span", title=True)
        # #female seed column
        # female_seeds_column = ""
        # for img in row.find_all(attrs={"width" : "12"}):
        #     female_seeds_column = img["title"]
        # Strain URL column
        strain_url_column = ""
        # Strain description column
        strain_description_column = ""
        
        th_classes = row.find('th', {'class': 'xs1'})
        xs1_children = th_classes.findChildren('a', recursive=False)
        for child in xs1_children:
            strain_url_column = child['href'].replace("../../../../", "https://en.seedfinder.eu/")
            strain_page = requests.get(strain_url_column).text
            strain_soup = BeautifulSoup(strain_page, "html.parser")
            # strain_table = strain_soup.find('div', class_='partInnerDiv')
            # if strain_table:
            #     for p in strain_table.find_all('p'):
            #         strain_description_column = p.text.strip() + "\n"
            # Parents column
            parents_column = ""
            straindb_column = ""
            parent1_column = ""
            parent2_column = ""
            grandparent1_1_column = ""
            grandparent1_2_column = ""
            grandparent2_2_column = ""
            grandparent2_2_column = ""
            parent2_column = ""
            parents_list_group = strain_soup.find('li', class_='Orig')
            if parents_list_group:
                parent_title = parents_list_group.text.strip()
                right_of_arrow, left_of_arrow = extract_text(parent_title)
                if ' x ' in right_of_arrow:
                    if right_of_arrow.split(' x ')[0]:
                        parent1_column = right_of_arrow.split(' x ')[0]
                    if right_of_arrow.split(' x ')[1]:
                        parent2_column = right_of_arrow.split(' x ')[1]
                    if left_of_arrow:
                        straindb_column = left_of_arrow
                        parents_column = f"{parent1_column},{parent2_column}"
                elif right_of_arrow:
                    parent1_column = right_of_arrow
                    parent2_column = right_of_arrow
                    if left_of_arrow:
                        straindb_column = left_of_arrow
                        parents_column = f"{parent1_column},{parent2_column}"

                # print(f"parent1_column {parent1_column} parent2_column {parent2_column} straindb_column {straindb_column}")
                # parents_list.append(parent1_column)
                # print(f"Parent list is: {parents_list}")
                # print(f"Parent 1 is: {parent1_column}")
                # print(f"Parent 2 is: {parent2_column}")
                # print(f"Left of arrow is: {straindb_column}")
            # data.append([strain_column[0].text.strip(), breeder_column[0].text.strip(), indica_sativa_column,
            #              indoor_outdoor_column, flowering_time_column[0]['title'], female_seeds_column,
            #              strain_url_column, strain_description_column, parents_column])
        # for child in xs1_children:
        #     strain_url_column = child['href'].replace("../../../../", "https://en.seedfinder.eu/")
        #     strain_page = requests.get(strain_url_column).text
        #     strain_soup = BeautifulSoup(strain_page, "html.parser")
        row_data = {}
        straindb_row_data = {}
        if parent1_column:
            straindb_row_data['Parent 1'] = parent1_column
        
        if parent2_column:
            straindb_row_data['Parent 2'] = parent2_column

        # if parent1_column:
        #     row_data['Parent 1'] = parent1_column
        
        # if parent2_column:
        #     row_data['Parent 2'] = parent2_column

        if straindb_column:
            straindb_row_data['Strain'] = straindb_column
        # print(f"{straindb_row_data['Strain']} {straindb_row_data['Parent 1']} {straindb_row_data['Parent 2']} ")

        # if strain_column:ç
        #     cannabis_strain = strain_column[0].text.strip()
        #     row_data['Cannabis Strain'] = cannabis_strain

        # if breeder_column:
        #     breeder = breeder_column[0].text.strip()
        #     row_data['Breeder'] = breeder

        # if indica_sativa_column:
        #     indica_sativa = indica_sativa_column
        #     row_data['Indica or Sativa'] = indica_sativa

        # if indoor_outdoor_column:
        #     indoor_outdoor = indoor_outdoor_column
        #     row_data['Indoor/Outdoor'] = indoor_outdoor

        # if flowering_time_column:
        #     flowering_time = flowering_time_column[0].text.strip()
        #     row_data['Flowering Time'] = flowering_time

        # if female_seeds_column:
        #     female_seeds = female_seeds_column
        #     row_data['Female Seeds'] = female_seeds

        # if strain_url_column:
        #     strain_url = strain_url_column
        #     row_data['Strain URL'] = strain_url
        
        # if strain_description_column:
        #     strain_description_replace_arrow = strain_description_column.replace("←", "<-")
        #     strain_description = strain_description_replace_arrow.replace("±", "+-")
        #     strain_description = ''.join(char for char in strain_description if char.isprintable())
        #     row_data['Strain Description'] = strain_description
        # if row_data:
        #     data.append(row_data)
        if straindb_row_data:
            dfs2.append(straindb_row_data)
    # if data:
    #     df = pd.DataFrame(data)
    #     dfs.append(df)
    # if straindb_row_data:
    #     # print(straindb_row_data)
    #     dfs2.append(straindb_row_data)
        # df2 = pd.DataFrame(straindb_row_data)
        # dfs2.append(df2)
        # print(dfs2)

# df = pd.concat(dfs, ignore_index=True)
# df = df.dropna()
# df.reset_index(drop=True, inplace=True)
df2 = pd.DataFrame(dfs2)
df2 = df2.dropna()
df2.reset_index(drop=True, inplace=True)
# dft_dictionary = df2.to_dict()
# df2 = pd.concat(dfs2, ignore_index=True)
# df2 = df2.dropna()
# df2.reset_index(drop=True, inplace=True)
# print(df.head(10))
# print(df2.head(10))

df2.to_excel("output.xlsx", index=False)


