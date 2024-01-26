#toutes gares : Paris, Lyon, Lille, Montpellier
#marhce pas : monaco, reims


import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import streamlit as st

def main():
    st.title("Ouigo Train Schedule Checker")

    # User inputs
    departure_city = st.text_input("Departure City", "Paris")
    arrival_city = st.text_input("Arrival City", "Lyon")
    day_match = st.text_input("Match Day (DD/MM/YY)", "04/01/24")

    if st.button("Search Trains"):
        df = get_train_schedule(departure_city, arrival_city, day_match)
        st.table(df)

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

    try:
        tout_autoriser_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        tout_autoriser_button.click()
    except Exception as e:
        print(f"Error clicking 'Tout autoriser' button: {e}")

    # Wait for the train containers to be present after accepting cookies
    train_containers=driver.find_elements(By.XPATH, '//div[@class="sc-iSlvIk jGrhNC"]')

    # Initialize lists to store data
    departure_times = []
    arrival_times = []
    departure_stations = []
    arrival_stations = []
    prices = []
    st.write('salut')
    # Loop through each train schedule entry
    for schedule_entry in train_containers:
        try:
            # Extract relevant details using Selenium
            departure_time = schedule_entry.find_element(By.XPATH, './/span[@class="sc-iHKyre eYmByj"][1]').text
            departure_station = schedule_entry.find_element(By.XPATH, './/span[@class="sc-fQvxEr bDVTWX"][1]').text
            arrival_time = schedule_entry.find_element(By.XPATH, './/span[@class="sc-iHKyre eYmByj"][2]').text
            arrival_station = schedule_entry.find_element(By.XPATH, './/span[@class="sc-fQvxEr bDVTWX"][2]').text
            price = schedule_entry.find_element(By.XPATH, './/span[contains(text(), "€")]').text

            # Append data to lists
            departure_times.append(departure_time)
            st.write( "salut")
            departure_stations.append(departure_station)
            arrival_times.append(arrival_time)
            arrival_stations.append(arrival_station)
            prices.append(price)
        except Exception as e:
            print(f"Error processing entry: {e}")
            continue

    # Create a DataFrame
    data = {
        'Departure Time': departure_times,
        'Departure Station': departure_stations,
        'Arrival Time': arrival_times,
        'Arrival Station': arrival_stations,
        'Price': prices
    }

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    main()


#cartographie des avions dans le monde avec les bilans carbone 
#carte lien entre 2 noeud empreinte carbone cumul par an 
#cartographie 
#mapx.orgx
#voir empreintes carbones qu on va avoir avec les JO
#voir trajet 
