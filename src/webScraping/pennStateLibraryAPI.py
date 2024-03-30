from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from webScraping.baseScraping import BaseScraping
import util.dictionaryValidationMethod as vd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class PennStateLibraryAPI(BaseScraping):

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
        service = ChromeService(ChromeDriverManager().install())
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

                self.driver.get(f"https://catalog.libraries.psu.edu/?search_field=all_fields&q={identifier}")

                time.sleep(5)

                try:

                    title = self.driver.find_element(By.CLASS_NAME, "index_title")
                    title_text = title.text[title.text.index(" ") + 1:]
                    link_to_title = self.driver.find_element(By.LINK_TEXT, title_text)
                    link_to_title.click()

                    time.sleep(5)

                    self.driver.get(self.driver.current_url + "/marc_view")

                    time.sleep(5)

                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body_text = body.text.replace("\n", " ")

                    try:
                        index_of_ocn = body_text.index("(OCoLC)")
                        self.catalog_data["OCN"] = body_text[index_of_ocn + 7: body_text.index(" ", index_of_ocn)]
                    except ValueError:
                        pass

                    def find_occurrences_using_index(input_string, search_string):
                        indices = []
                        start_index = 0

                        while True:
                            try:
                                index = input_string.index(search_string, start_index)
                                indices.append(index)
                                start_index = index + 1
                            except ValueError:
                                break

                        return indices

                    indexes_of_fifty_part_one = find_occurrences_using_index(body_text, "050    4 ")
                    indexes_of_fifty_part_two = find_occurrences_using_index(body_text, "050 1 4")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = body_text.index("a| ", index_of_fifty)
                        first_portion = body_text[
                                        index_of_first_portion + 3: body_text.index(" ", index_of_first_portion + 3)]
                        index_of_second_portion = body_text.index("b| ", index_of_fifty)
                        index_of_intermediate_space = body_text.index(" ", index_of_second_portion + 3)
                        index_of_final_space = body_text.index(" ", index_of_intermediate_space + 1)
                        second_portion = body_text[index_of_second_portion + 3: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = body_text.index(" ", index_of_first_portion + 3)
                        if body_text[index_of_filter_space + 1: index_of_filter_space + 4] != "b| ":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Penn_State")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(f"https://catalog.libraries.psu.edu/?search_field=all_fields&q={identifier}")

                time.sleep(5)

                try:

                    title = self.driver.find_element(By.CLASS_NAME, "index_title")
                    title_text = title.text[title.text.index(" ") + 1:]
                    link_to_title = self.driver.find_element(By.LINK_TEXT, title_text)
                    link_to_title.click()

                    time.sleep(5)

                    try:
                        isbn_list = self.driver.find_element(By.CLASS_NAME, "blacklight-isbn_ssm")
                        isbn_list = isbn_list.text.split("\n")
                        for isbn in isbn_list:
                            try:
                                isbn = isbn[:isbn.index(" ")]
                                self.catalog_data["ISBN"].append(isbn)
                            except ValueError:
                                self.catalog_data["ISBN"].append(isbn)
                    except NoSuchElementException:
                        pass

                    self.driver.get(self.driver.current_url + "/marc_view")

                    time.sleep(5)

                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body_text = body.text.replace("\n", " ")

                    def find_occurrences_using_index(input_string, search_string):
                        indices = []
                        start_index = 0

                        while True:
                            try:
                                index = input_string.index(search_string, start_index)
                                indices.append(index)
                                start_index = index + 1
                            except ValueError:
                                break

                        return indices

                    indexes_of_fifty_part_one = find_occurrences_using_index(body_text, "050    4 ")
                    indexes_of_fifty_part_two = find_occurrences_using_index(body_text, "050 1 4")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = body_text.index("a| ", index_of_fifty)
                        first_portion = body_text[
                                        index_of_first_portion + 3: body_text.index(" ", index_of_first_portion + 3)]
                        index_of_second_portion = body_text.index("b| ", index_of_fifty)
                        index_of_intermediate_space = body_text.index(" ", index_of_second_portion + 3)
                        index_of_final_space = body_text.index(" ", index_of_intermediate_space + 1)
                        second_portion = body_text[index_of_second_portion + 3: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = body_text.index(" ", index_of_first_portion + 3)
                        if body_text[index_of_filter_space + 1: index_of_filter_space + 4] != "b| ":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Penn_State")

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