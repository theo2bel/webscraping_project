import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import re
import requests
from bs4 import BeautifulSoup


#Matchs que nous avons récupérés auparavant

data = {
    'Type_match': ['Ligue 1', 'Ligue 1', 'Ligue 1', 'Champions League', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Champions League', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1', 'Ligue 1'],
    'Date_match': ['28.01', '2.02', '11.02', '14.02', '18.02', '25.02', '3.03', '5.03', '10.03', '17.03', '31.03', '7.04', '14.04', '21.04', '28.04', '4.05', '11.05', '18.05'],
    'Equipe_domicile': ['Paris SG', 'Strasbourg', 'Paris SG', 'Paris SG', 'Nantes', 'Paris SG', 'Monaco', 'Real Sociedad', 'Paris SG', 'Montpellier', 'Marseille', 'Paris SG', 'Lorient', 'Paris SG', 'Paris SG', 'Nice', 'Paris SG', 'Metz'],
    'Equipe_exterieur': ['Brest', 'Paris SG', 'Lille', 'Real Sociedad', 'Paris SG', 'Rennes', 'Paris SG', 'Real Sociedad', 'Reims', 'Paris SG', 'Paris SG', 'Clermont Foot', 'Paris SG', 'Lyon', 'Le Havre', 'Paris SG', 'Toulouse', 'Paris SG'],
    'Latitude_domicile': [48.8566, 48.5734, 48.8566, 48.8566, 47.2184, 48.8566, 43.7384, 43.2965, 48.8566, 43.6110, 43.2965, 48.8566, 47.7482, 48.8566, 48.8566, 43.7102, 48.8566, 49.1193],
    'Longitude_domicile': [2.3522, 7.7521, 2.3522, 2.3522, -1.5536, 2.3522, 7.4246, 5.3698, 2.3522, 3.8767, 5.3698, 2.3522, -3.3701, 2.3522, 2.3522, 7.2620, 2.3522, 6.1757],
    'Latitude_exterieur': [48.8566] * 18,
    'Longitude_exterieur': [2.3522] * 18  
}

df=pd.DataFrame(data)

#We only keep the matches outside of paris
df = df[(df['Equipe_exterieur'] == 'Paris SG') & (df['Type_match'] == 'Ligue 1')]

# Drop rows with missing values
df = df.dropna()

#st.table(df)

# Streamlit app
st.image('Paris_Saint-Germain_Logo.svg.png',width=100)

st.title('Transport proposition for PSG')

# Display the list of matches in the dropdown
selected_match_index = st.selectbox('Choose a match:', df['Type_match'] + ' - ' + df['Date_match'] + ' - ' + df['Equipe_domicile'] + ' vs ' + df['Equipe_exterieur'])

# Retrieve the selected match data using the index
selected_match_data = df.loc[df.index[df['Type_match'] + ' - ' + df['Date_match'] + ' - ' + df['Equipe_domicile'] + ' vs ' + df['Equipe_exterieur'] == selected_match_index].values[0]]

# Display the selected match details

st.write(f"Selected Match Details:")
st.write(f"Type: {selected_match_data[0]}")
st.write(f"Date: {selected_match_data[1]}")
st.write(f"Teams: {selected_match_data[2]} vs {selected_match_data[3]}")








#Adding the carbon foot print of the plane for those destinations




#Scraping du site "https://www.techno-science.net/definition/12174.html" pour récupérer les aéroports de France


url = "https://www.techno-science.net/definition/12174.html"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})

rows = table.find_all('tr')
data = []
for row in rows:
    cols = row.find_all('td')
    if cols:
        # Extraction des colonnes 'Code AITA', 'Nom de l'aérodrome' et 'Ville desservie'
        data.append([cols[0].text.strip(), cols[2].text.strip(), cols[3].text.strip()])

column_names = ["Code AITA", "Nom de l'aérodrome", "Ville desservie"]
df = pd.DataFrame(data, columns=column_names)


#Code pour récupérer dans le dataframe le code AITA si on lui donne la ville

def find_aita_code(city_name, df):
    result = df[df['Ville desservie'].str.contains(city_name, case=False, na=False)]
    if not result.empty:
        return result.iloc[0]['Code AITA']
    else:
        return None


#Scraping de carbonfootprint pour récupérer l'empreinte carbone en avion de deux villes


departure_city =selected_match_data[3].split(" ")[0] 
#for Paris SG we only want Paris : the city
arrival_city = selected_match_data[2]

def wait_for_element(by, value, timeout=10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((by, value)))

depart_aita_code = find_aita_code(departure_city, df)
arrive_aita_code = find_aita_code(arrival_city, df)

if depart_aita_code and arrive_aita_code:
    driver = webdriver.Firefox()
    driver.get("https://calculator.carbonfootprint.com/calculator.aspx?tab=3")

    arrival_field = wait_for_element(By.ID, "ctl05_rcbAirportTo_Input")
    arrival_field.clear()
    arrival_field.send_keys(arrive_aita_code)
    arrival_field.send_keys(Keys.TAB)

    arrow_element = wait_for_element(By.ID, "ctl05_rcbAirportTo_Arrow")
    arrow_element.click()

    departure_field = wait_for_element(By.ID, "ctl05_rcbAirportFrom_Input")
    departure_field.clear()
    departure_field.send_keys("PAR")
    departure_field.send_keys(Keys.TAB)

    arrow_element_departure = wait_for_element(By.ID, "ctl05_rcbAirportFrom_Arrow")
    arrow_element_departure.click()

    actions = ActionChains(driver)
    calculate_button = wait_for_element(By.ID, "ctl05_btnAddFlight")
    actions.move_to_element(calculate_button).click().perform()

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "table.footprints"))
        )
        carbon_footprint_element = driver.find_element(By.CSS_SELECTOR, "table.footprints td:first-child")
        carbon_footprint_text = carbon_footprint_element.text
        match = re.search(r"([\d.]+)\s*metric tons", carbon_footprint_text)
        carbon_footprint = match.group(1) if match else "Non trouvé"
        carbon_footprint_kgrams=float(carbon_footprint)*1000
    except Exception as e:
        print("Une erreur est survenue :", e)

    st.write("Carbon foot print if taking the plane :", carbon_footprint_kgrams, "metric kilograms of CO2")

    driver.quit()
else:
    print("Les codes AITA pour les villes fournies n'ont pas été trouvés.")


#Adding the footprint of train 



# we retrieve the distance as the crow flies between the 2 cities to calculate the foot print of the train

from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of Earth in kilometers (change to 3958.8 miles for statute miles)
    radius = 6371.0

    # Calculate the distance
    distance = radius * c

    return int(distance)

distance_train=haversine(selected_match_data[4],selected_match_data[5],selected_match_data[6],selected_match_data[7])

#footprint of the train : 2.4 g/km

foot_print_train=round(distance_train*(2.4/1000),2)

st.write("Carbon foot print if taking the train :", foot_print_train, "metric kilograms of CO2")

rapport=int(carbon_footprint_kgrams/foot_print_train)
st.write("The plane foot print is "+str(rapport)+" times bigger than the train one for this destination")






map_center = [(selected_match_data[4] + selected_match_data[6]) / 2,
              (selected_match_data[5] + selected_match_data[7]) / 2]

my_map = folium.Map(location=map_center, zoom_start=6)

# Add markers for both cities
folium.Marker(location=[selected_match_data[4], selected_match_data[5]],
              popup=f"{selected_match_data[2]}").add_to(my_map)

folium.Marker(location=[selected_match_data[6], selected_match_data[7]],
              popup=f"{selected_match_data[3]}").add_to(my_map)

# Add PolyLines for both train and plane routes
plane_line_coords = [
    [selected_match_data[4] + 0.1, selected_match_data[5] + 0.1],  # Adjusted latitude
    [selected_match_data[6] + 0.1, selected_match_data[7] + 0.1]   # Adjusted latitude
]
folium.PolyLine(locations=plane_line_coords, color='red', weight=4, opacity=1,
                popup='Plane').add_to(my_map)

# Add a line connecting the cities for the train route
train_line_coords = [
    [selected_match_data[4], selected_match_data[5]],
    [selected_match_data[6], selected_match_data[7]]
]
folium.PolyLine(locations=train_line_coords, color='green', weight=2, opacity=1,
                popup='Train').add_to(my_map)

# Display the legend
my_map.add_child(folium.LayerControl())

# Display the map
st.write("Match Location Map:")
folium_static(my_map)

















#Adding the table of trains from paris to the arrival city by scrapping ouigo.com

def get_train_schedule(departure_city, arrival_city, day_match):
    date_object = datetime.strptime(day_match, "%d/%m/%y")
    day_before = date_object - timedelta(days=1)
    day_arrival = day_before.strftime("%d/%m/%y")



    #we launch the driver
    driver = webdriver.Firefox()
    driver.get("https://www.ouigo.com/")

    # We wait for the page to be displayed
    def wait_for_element(by, value):
        return WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by, value))
        )

    # We write the origin station
    origin_input_field = wait_for_element(By.ID, "origin-station-input-field__input")
    origin_input_field.clear()
    if departure_city in ['Paris','Lyon','Lille','Montpellier']:
        origin_input_field.send_keys(departure_city+" toutes gares")
    else:
        origin_input_field.send_keys(departure_city)

    # Find and interact with the destination station input field
    destination_input_field = wait_for_element(By.ID, "destination-station-input-field__input")
    destination_input_field.clear()
    if arrival_city in ['Paris','Lyon','Lille','Montpellier']:
        destination_input_field.send_keys(arrival_city+" toutes gares")
    else:
        destination_input_field.send_keys(arrival_city)

    # The date we want to take the train
    current_date_string = day_arrival

    # Split the date string into day, month, and year
    day, month, year = current_date_string.split('/')

    #We do it twice because there if we do it once, the date is added to the current date so it does not work
    for i in range(2):
        outbound_date_input_field = wait_for_element(By.ID, "search-engine__inputfield__outbound-date__input")
        driver.execute_script("arguments[0].value='';", outbound_date_input_field)
        outbound_date_input_field.send_keys(day + "/" + month + "/" + year)

    #We click on the button to search for the trains that correspond to the criteria we gave
    for i in range(6):
            try:
                refresh_button = wait_for_element(By.XPATH, '//button[@title="Actualiser le trajet"]')
                refresh_button.click()
            except:
                # If StaleElementReferenceException is thrown, the page has changed, so continue the loop
                break

    html_string = driver.page_source

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Find all elements with the specified class
    elements = soup.find_all('div', class_='sc-iSlvIk jGrhNC')
    
    # Initialize lists to store data
    departure_times = []
    departure_stations = []
    arrival_times = []
    arrival_stations = []
    prices = []
    
    # Loop through each element to extract information
    for element in elements:
        departure_time = element.find('span', class_='sc-iHKyre eYmByj').text
        departure_station = element.find_all('span', class_='sc-fQvxEr bDVTWX')[0].text
        arrival_time = element.find_all('span', class_='sc-iHKyre eYmByj')[-1].text
        arrival_station = element.find_all('span', class_='sc-fQvxEr bDVTWX')[1].text

        try:
            price = element.find('span', class_='sc-cZbmGM gmICRw').text.strip()
        except:
            price = element.find('span', class_='sc-cZbmGM cCOdkP').text.strip()

        
    
        # Append data to respective lists
        departure_times.append(departure_time)
        departure_stations.append(departure_station)
        arrival_times.append(arrival_time)
        arrival_stations.append(arrival_station)
        prices.append(price)
    
    # Create the data dictionary
    data = {
        'Departure Time': departure_times,
        'Departure Station': departure_stations,
        'Arrival Time': arrival_times,
        'Arrival Station': arrival_stations,
        'Price': prices
    }
    # Replace the final line that creates the DataFrame with:
    return pd.DataFrame(data)


departure_city = selected_match_data[3].split(" ")[0]#for Paris SG we only want Paris
arrival_city = selected_match_data[2]
day_match = "/".join(selected_match_data[1].split('.'))+"/24"
train_df = get_train_schedule(departure_city, arrival_city, day_match)
st.table(train_df)

st.write("Moreover, the train is really cheap for this destination, and not much longer")
st.write("So they should definitely take the train for this destination ! ")


