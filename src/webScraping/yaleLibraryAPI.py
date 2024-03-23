from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from .baseScraping import BaseScraping
import src.util.dictionaryValidationMethod as vd


class YaleLibraryAPI(BaseScraping):

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

                self.driver.get(f"https://search.library.yale.edu/quicksearch?q={identifier}&commit=Search")

                time.sleep(5)

                try:
                    title = self.driver.find_element(By.CLASS_NAME, "result_title")
                    printable_title = title.text
                    link = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link.click()

                    time.sleep(5)

                    intermediate_url = self.driver.current_url[:self.driver.current_url.index("?")]
                    self.driver.get(f"{intermediate_url}/librarian_view")

                    body_element = self.driver.find_element(By.TAG_NAME, 'body')
                    webpage_text = body_element.text.replace("\n", " ")

                    try:
                        index_of_ocn = webpage_text.index("(OCoLC)")
                        self.catalog_data["OCN"] = webpage_text[index_of_ocn + 7: webpage_text.index(" ", index_of_ocn)]
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
                    indexes_of_fifty_part_two = find_occurrences_using_index(webpage_text, "050    0")
                    indexes_of_fifty_part_three = find_occurrences_using_index(webpage_text, "050 0 0")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two + indexes_of_fifty_part_three

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = webpage_text.index("|a ", index_of_fifty)
                        first_portion = webpage_text[
                                        index_of_first_portion + 3: webpage_text.index(" ", index_of_first_portion + 3)]
                        index_of_second_portion = webpage_text.index("|b ", index_of_fifty)
                        index_of_intermediate_space = webpage_text.index(" ", index_of_second_portion + 3)
                        index_of_final_space = webpage_text.index(" ", index_of_intermediate_space + 1)
                        second_portion = webpage_text[index_of_second_portion + 3: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = webpage_text.index(" ", index_of_first_portion + 3)
                        if webpage_text[index_of_filter_space + 1: index_of_filter_space + 4] != "|b ":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Yale")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(f"https://search.library.yale.edu/quicksearch?q={identifier}&commit=Search")

                time.sleep(6)

                try:
                    title = self.driver.find_element(By.CLASS_NAME, "result_title")
                    printable_title = title.text
                    link = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link.click()

                    time.sleep(5)

                    intermediate_url = self.driver.current_url[:self.driver.current_url.index("?")]
                    self.driver.get(f"{intermediate_url}/librarian_view")

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
                            if webpage_text.index("|z", index_of_twenty) < webpage_text.index("|a", index_of_twenty):
                                index_of_z = webpage_text.index("|z", index_of_twenty)
                                self.catalog_data["ISBN"].append(
                                    webpage_text[index_of_z + 3: webpage_text.index(" ", index_of_z + 3)])
                            else:
                                index_of_a = webpage_text.index("|a", index_of_twenty)
                                self.catalog_data["ISBN"].append(
                                    webpage_text[index_of_a + 3: webpage_text.index(" ", index_of_a + 3)])
                        except ValueError:
                            pass

                    indexes_of_fifty_part_one = find_occurrences_using_index(webpage_text, "050    4")
                    indexes_of_fifty_part_two = find_occurrences_using_index(webpage_text, "050    0")
                    indexes_of_fifty_part_three = find_occurrences_using_index(webpage_text, "050 0 0")
                    indexes_of_fifty_part_four = find_occurrences_using_index(webpage_text, "050       ")
                    indexes_of_fifty_part_five = find_occurrences_using_index(webpage_text, "050 0    ")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two + indexes_of_fifty_part_three
                    indexes_of_fifty += indexes_of_fifty_part_four
                    indexes_of_fifty += indexes_of_fifty_part_five

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = webpage_text.index("|a ", index_of_fifty)
                        first_portion = webpage_text[
                                        index_of_first_portion + 3: webpage_text.index(" ", index_of_first_portion + 3)]
                        index_of_second_portion = webpage_text.index("|b ", index_of_fifty)
                        index_of_intermediate_space = webpage_text.index(" ", index_of_second_portion + 3)
                        index_of_final_space = webpage_text.index(" ", index_of_intermediate_space + 1)
                        second_portion = webpage_text[index_of_second_portion + 3: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = webpage_text.index(" ", index_of_first_portion + 3)
                        if webpage_text[index_of_filter_space + 1: index_of_filter_space + 4] != "|b ":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("Yale")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

        except WebDriverException:
            # print(f"Browser session has been closed or lost: {e}")
            self.driver = webdriver.Chrome()
            return {k.lower(): v for k, v in self.catalog_data.items()}
