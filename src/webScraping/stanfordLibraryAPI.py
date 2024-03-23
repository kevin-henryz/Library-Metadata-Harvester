from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from .baseScraping import BaseScraping
import src.util.dictionaryValidationMethod as vd


class StanfordLibraryAPI(BaseScraping):

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

                self.driver.get(f"https://searchworks.stanford.edu/?search_field=search&q={identifier}")

                time.sleep(5)

                try:
                    # Get the title of the catalog item and click on it.
                    title = self.driver.find_element(By.XPATH, '//*[@itemprop="name"]')
                    printable_title = title.text
                    link_to_book = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link_to_book.click()

                    time.sleep(4)

                    # View the item in the librarian view.
                    self.driver.get(self.driver.current_url + "/librarian_view")

                    time.sleep(4)

                    # Get the relevant text from the website's body
                    dropdown_element = self.driver.find_element(By.CLASS_NAME, "mb-3")
                    dropdown_element.click()
                    body_element = self.driver.find_element(By.TAG_NAME, 'body')
                    webpage_text = body_element.text.replace("\n", " ")

                    try:
                        index_of_ocn = webpage_text.index("(OCoLC)")
                        self.catalog_data["OCN"] = webpage_text[index_of_ocn + 7: webpage_text.index(" ", index_of_ocn)]
                    except ValueError:
                        try:
                            index_of_ocn = webpage_text.index("(OCoLC-M)")
                            self.catalog_data["OCN"] = webpage_text[
                                                       index_of_ocn + 9: webpage_text.index(" ", index_of_ocn)]
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

                    indexes_of_fifty_part_one = find_occurrences_using_index(webpage_text, "050    4")
                    indexes_of_fifty_part_two = find_occurrences_using_index(webpage_text, "050 0 4")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two

                    for index_of_fifty in indexes_of_fifty:
                        # Formatting to get LCCN Parts
                        index_of_first_portion = webpage_text.index("a|", index_of_fifty)
                        index_of_second_potion = webpage_text.index("b|", index_of_fifty)
                        index_of_intermediate_space = webpage_text.index(" ", index_of_second_potion + 3)
                        index_of_final_space = webpage_text.index(" ", index_of_intermediate_space + 1)
                        first_portion = webpage_text[
                                        index_of_first_portion + 3: webpage_text.index(" ", index_of_first_portion + 3)]
                        second_portion = webpage_text[index_of_second_potion + 3: index_of_final_space]
                        # Add parts together.
                        lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Stanford")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(f"https://searchworks.stanford.edu/?search_field=search&q={identifier}")

                time.sleep(5)

                try:

                    # Get the title of the catalog item and click on it.
                    title = self.driver.find_element(By.XPATH, '//*[@itemprop="name"]')
                    printable_title = title.text
                    link_to_book = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link_to_book.click()

                    time.sleep(4)

                    # View the item in the librarian view.
                    self.driver.get(self.driver.current_url + "/librarian_view")

                    time.sleep(4)

                    # Get the relevant text from the website's body
                    dropdown_element = self.driver.find_element(By.CLASS_NAME, "mb-3")
                    dropdown_element.click()
                    body_element = self.driver.find_element(By.TAG_NAME, 'body')
                    webpage_text = body_element.text.replace("\n", " ")

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

                    indexes_of_twenty = find_occurrences_using_index(webpage_text, "020       ")
                    for index_of_twenty in indexes_of_twenty:
                        try:
                            if webpage_text.index("z|", index_of_twenty) < webpage_text.index("a|", index_of_twenty):
                                index_of_z = webpage_text.index("z|", index_of_twenty)
                                self.catalog_data["ISBN"].append(
                                    webpage_text[index_of_z + 3: webpage_text.index(" ", index_of_z + 3)])
                            else:
                                index_of_a = webpage_text.index("a|", index_of_twenty)
                                self.catalog_data["ISBN"].append(
                                    webpage_text[index_of_a + 3: webpage_text.index(" ", index_of_a + 3)])
                        except ValueError:
                            pass

                    indexes_of_fifty_part_one = find_occurrences_using_index(webpage_text, "050    4")
                    indexes_of_fifty_part_two = find_occurrences_using_index(webpage_text, "050 0 4")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two

                    for index_of_fifty in indexes_of_fifty:
                        # Formatting to get LCCN Parts
                        index_of_first_portion = webpage_text.index("a|", index_of_fifty)
                        index_of_second_potion = webpage_text.index("b|", index_of_fifty)
                        index_of_intermediate_space = webpage_text.index(" ", index_of_second_potion + 3)
                        index_of_final_space = webpage_text.index(" ", index_of_intermediate_space + 1)
                        first_portion = webpage_text[
                                        index_of_first_portion + 3: webpage_text.index(" ", index_of_first_portion + 3)]
                        second_portion = webpage_text[index_of_second_potion + 3: index_of_final_space]
                        # Add parts together.
                        lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Stanford")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

        except WebDriverException:
            # print(f"Browser session has been closed or lost: {e}")
            self.driver = webdriver.Chrome()
            return {k.lower(): v for k, v in self.catalog_data.items()}
