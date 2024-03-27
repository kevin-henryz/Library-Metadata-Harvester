from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from webScraping.baseScraping import BaseScraping
import util.dictionaryValidationMethod as vd
from selenium.webdriver.chrome.service import Service
import os


class DukeLibraryAPI(BaseScraping):

    def __init__(self):
        self.initialize_driver()
        self.catalog_data = {"ISBN": [], "OCN": "", "LCCN": [], "LCCN_Source": []}

    def initialize_driver(self):
        """Initializes the Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        service = Service(log_path=os.devnull)
        self.driver = webdriver.Chrome(service=service, options=options)

    def close_driver(self):
        """Safely closes the driver and quits the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def send_dictionary(self):
        self.catalog_data = vd.optimize_dictionary(self.catalog_data)
        return {k.lower(): v for k, v in self.catalog_data.items()}

    def fetch_metadata(self, identifier, input_type):

        try:

            self.catalog_data = {"ISBN": [], "OCN": "", "LCCN": [], "LCCN_Source": []}
            if not self.is_online():
                print("No internet connection available at the start.")
                return self.send_dictionary() 
            identifier = identifier.strip("\n")
            input_type = input_type.upper()

            if (input_type != "OCN") and (input_type != "ISBN"):
                # print("Please select either 'ISBN' or 'OCN' as your second argument.")
                return {k.lower(): v for k, v in self.catalog_data.items()}

            elif input_type == "ISBN":

                self.catalog_data["ISBN"].append(identifier)

                self.driver.get(f"https://find.library.duke.edu/?utf8=%E2%9C%93&search_field=isbn_issn&q={identifier}")

                time.sleep(5)

                try:
                    title = self.driver.find_element(By.CLASS_NAME, "index_title")
                    title_text = title.text[title.text.index(" ") + 1:]
                    link_to_title = self.driver.find_element(By.LINK_TEXT, title_text)
                    link_to_title.click()

                    time.sleep(5)

                    try:
                        lccn = self.driver.find_element(By.CLASS_NAME, "call-number").text
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Duke")
                    except NoSuchElementException:
                        pass

                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        body_text = body.text.replace("\n", " ")
                        index_of_oclc = body_text.index("OCLC Number: ")
                        ocn = body_text[index_of_oclc + 13: body_text.index(" ", index_of_oclc + 13)]
                        self.catalog_data["OCN"] = ocn
                    except ValueError:
                        pass

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(
                    f"https://find.library.duke.edu/?utf8=%E2%9C%93&f%5Bresource_type_f%5D%5B%5D=Book&search_field=all_fields&q={identifier}")

                time.sleep(5)

                try:
                    title = self.driver.find_element(By.CLASS_NAME, "index_title")
                    title_text = title.text[title.text.index(" ") + 1:]
                    link_to_title = self.driver.find_element(By.LINK_TEXT, title_text)
                    link_to_title.click()

                    time.sleep(5)

                    try:
                        lccn = self.driver.find_element(By.CLASS_NAME, "call-number").text
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Duke")
                    except NoSuchElementException:
                        pass

                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        body_text = body.text.replace("\n", " ")
                        index_of_isbn = body_text.index("ISBN: ")
                        index_of_end_of_relevant_text = body_text.index(":", index_of_isbn + 6)
                        relevant_items = body_text[index_of_isbn + 6: index_of_end_of_relevant_text].split(" ")

                        def contains_digits(input_string):
                            return any(char.isdigit() for char in input_string)

                        for item in relevant_items:
                            if contains_digits(item):
                                self.catalog_data["ISBN"].append(item)
                    except ValueError:
                        pass

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

        except WebDriverException:
            # print(f"Browser session has been closed or lost: {e}")
            self.close_driver()  # Close the current driver due to the exception
            self.initialize_driver()
            print(f"Encountered a WebDriverException, possibly due to network issues: {e}")
            return self.send_dictionary() 
        except Exception as e:
            # Handle other generic exceptions if necessary
            return self.send_dictionary() 
