import csv
import time


def get_data(url: str, element_to_find: str):
    "Scrape data from a target website using selenium and format it to a dictionary"

    from selenium import webdriver
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.by import By

    element_dict = {}

    # Use chrome for the data scraping other browsers might also be fine, but not tested
    # Selenium is used since the example site loads certain content with JavaScript
    browser = webdriver.Chrome()
    browser.get(url)

    # Try to get find an element, the site might take time load so retry a few times.
    for x in range(5):
        try:
            # Getting the name of the element that hold the data with it's xPATH
            site_element = browser.find_element(By.XPATH, element_to_find)
            print("Element found")
            break
        except:
            # If the element is not found wait and retry incase it simply didn't load in time.
            print("Failed to retrieve element, retrying")
            time.sleep(1)

    # Scroll the list down to load all entries
    for x in range(10):
        ActionChains(browser)\
            .send_keys_to_element(site_element, ("\uE015	"))\
            .perform()

    # site_element's child elements with the span tag
    child_elements = site_element.find_elements(By.TAG_NAME, "span")

    # Initial entry key
    id = 1

    for entry in child_elements:
        # the data is stored in four "columns" with td tag
        # add the columns to a list and then to a dictionary, clear the list and repeat
        entry_column = entry.find_elements(By.TAG_NAME, "td")
        element_list = [x.text for x in entry_column]
        element_dict = {column_names[0]: element_list[0],
                        column_names[1]: element_list[1],
                        column_names[2]: element_list[2],
                        column_names[3]: element_list[3],
                        column_names[4]: element_list[4]}
        
        element_list.clear()
        # Store dictionaries in a list with the appropriate key
        country_list.append(element_dict)
        id += 1

    browser.quit()


# Write the extracted data to a csv
def write_csv(file_name: str):
    
    with open(file_name, 'w') as csvfile:
        # restval is used if dictionary is missing a key
        csv_writer = csv.DictWriter(
            csvfile, fieldnames=column_names, restval='null')
        csv_writer.writeheader()
        csv_writer.writerows(country_list)


if __name__ == '__main__':

    column_names = ['Rank', 'Country', 'Cost Index',
                    'Monthly Income', 'Purchasing Power Index']
    country_list = []
    site_url = "https://www.kaggle.com/datasets/meeratif/global-income-purchasing-power/data"

    # HTML element to be extracted. Example is an xPATH, but selenium accepots other identifiers as well
    element_to_find = "/html/body/div[2]/div[1]/div[2]/div/div[2]/div/div[5]/div[2]/div/div/div[1]/div/div[3]/div[6]"
    
    get_data(site_url, element_to_find)
    write_csv('scrapped_data.csv')
