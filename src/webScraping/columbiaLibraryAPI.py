from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from .baseScraping import BaseScraping

class ColumbiaLibraryAPI(BaseScraping):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode.
        options.add_argument('--no-sandbox')  # Bypass OS security model.
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems.
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.catalog_data = {"ISBN": [], "OCN": "", "LCCN": [], "LCCN_Source": []}

    def fetch_metadata(self, identifier, input_type):

        try:

            self.catalog_data = {"ISBN": [], "OCN": "", "LCCN": [], "LCCN_Source": []}
            identifier = identifier.strip("\n")
            input_type = input_type.upper()

            if (input_type != "OCN") and (input_type != "ISBN"):
                # print("Please select either 'ISBN' or 'OCN' as your second argument.")
                return {k.lower(): v for k, v in self.catalog_data.items()}

            elif input_type == "ISBN":

                self.catalog_data["ISBN"].append(identifier)

                self.driver.get(f"https://clio.columbia.edu/quicksearch?q={identifier}&commit=Search")

                time.sleep(5)

                try:
                    catalog = self.driver.find_element(By.CLASS_NAME, "result_set")

                    intermediate_step = catalog.find_elements(By.CLASS_NAME, "result")

                    if len(intermediate_step) == 0:
                        # print(f"ISBN {identifier} has no associated catalog in Columbia.")
                        return {k.lower(): v for k, v in self.catalog_data.items()}

                    max_length = 0
                    index_of_desired_element = 0

                    for element in intermediate_step:
                        information_list = element.get_attribute('standard_ids')

                        information_list = information_list.strip("[]").replace("oclc", "ocn")
                        information_list = information_list.replace('"', '').replace(':', ': ').upper()
                        list_format = information_list.split(", ")

                        if len(list_format) > max_length:
                            max_length = len(list_format)
                            index_of_desired_element = intermediate_step.index(element)

                    desired_element = intermediate_step[index_of_desired_element]

                    information_list = desired_element.get_attribute('standard_ids')

                    information_list = information_list.strip("[]").replace("oclc", "ocn")
                    information_list = information_list.replace('"', '').replace(':', ': ').upper()
                    list_format = information_list.split(", ")

                    for item in list_format:
                        if 'OCN' in item:
                            if self.catalog_data["OCN"] == "":
                                self.catalog_data["OCN"] = item[5:]
                        elif "LCCN" in item:
                            self.catalog_data["LCCN"].append(item[6:])
                            self.catalog_data["LCCN_Source"].append("Columbia")

                    return {k.lower(): v for k, v in self.catalog_data.items()}

                except NoSuchElementException:
                    # print(f"Error for ISBN {identifier} when entered into Columbia: {e}")
                    return {k.lower(): v for k, v in self.catalog_data.items()}

                except ValueError:
                    return {k.lower(): v for k, v in self.catalog_data.items()}

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(f"https://clio.columbia.edu/quicksearch?q={identifier}&commit=Search")

                time.sleep(5)

                try:
                    catalog = self.driver.find_element(By.CLASS_NAME, "result_set")

                    intermediate_step = catalog.find_elements(By.CLASS_NAME, "result")

                    if len(intermediate_step) == 0:
                        # print(f"OCN {identifier} has no associated catalog in Columbia.")
                        return {k.lower(): v for k, v in self.catalog_data.items()}

                    max_length = 0
                    index_of_desired_element = 0

                    for element in intermediate_step:
                        information_list = element.get_attribute('standard_ids')

                        information_list = information_list.strip("[]").replace("oclc", "ocn")
                        information_list = information_list.replace('"', '').replace(':', ': ').upper()
                        list_format = information_list.split(", ")

                        if len(list_format) > max_length:
                            max_length = len(list_format)
                            index_of_desired_element = intermediate_step.index(element)

                    desired_element = intermediate_step[index_of_desired_element]

                    information_list = desired_element.get_attribute('standard_ids')

                    information_list = information_list.strip("[]").replace("oclc", "ocn")
                    information_list = information_list.replace('"', '').replace(':', ': ').upper()
                    list_format = information_list.split(", ")

                    for item in list_format:
                        if 'ISBN' in item:
                            self.catalog_data["ISBN"].append(item[6:])
                        elif "LCCN" in item:
                            self.catalog_data["LCCN"].append(item[6:])
                            self.catalog_data["LCCN_Source"].append("Columbia")

                    return {k.lower(): v for k, v in self.catalog_data.items()}

                except NoSuchElementException:
                    # print(f"Error for OCN {identifier} when entered into Columbia: {e}")
                    return {k.lower(): v for k, v in self.catalog_data.items()}

                except ValueError:
                    return {k.lower(): v for k, v in self.catalog_data.items()}

        except WebDriverException:
            # print(f"Browser session has been closed or lost: {e}")
            self.driver = webdriver.Chrome()
            return {k.lower(): v for k, v in self.catalog_data.items()}