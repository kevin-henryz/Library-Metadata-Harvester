from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from webScraping.baseScraping import BaseScraping
import util.dictionaryValidationMethod as vd


class DukeLibraryAPI(BaseScraping):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode.
        options.add_argument('--no-sandbox')  # Bypass OS security model.
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems.
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.catalog_data = {"ISBN": [], "OCN": "", "LCCN": [], "LCCN_Source": []}

    def send_dictionary(self):
        self.catalog_data = vd.optimize_dictionary(self.catalog_data)
        return {k.lower(): v for k, v in self.catalog_data.items()}

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
            self.driver = webdriver.Chrome()
            return {k.lower(): v for k, v in self.catalog_data.items()}
