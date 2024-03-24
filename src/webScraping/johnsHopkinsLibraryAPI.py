from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.common.exceptions import WebDriverException
from .baseScraping import BaseScraping
import src.util.dictionaryValidationMethod as vd


class JohnsHopkinsLibraryAPI(BaseScraping):

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
        print(self.catalog_data)
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

                self.driver.get(
                    f"https://catalyst.library.jhu.edu/discovery/search?query=any,contains,{identifier}&pfilter=rtype,exact,books&tab=Everything&search_scope=MyInst_and_CI&vid=01JHU_INST:JHU&offset=0")

                time.sleep(5)

                try:
                    title = self.driver.find_element(By.TAG_NAME, 'prm-highlight')
                    printable_title = title.text
                    link_to_book = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link_to_book.click()

                    time.sleep(5)

                    # Unfortunately, the current url has limitations regarding its web scraping accommodations.
                    # Get the necessary information from the current url to access a new url.
                    url = self.driver.current_url
                    index_vid = url.index("vid")
                    index_doc = url.index("docid")
                    vid = url[index_vid + 4: url.index("&", index_vid)]
                    doc = url[index_doc + 6: url.index("&", index_doc)]
                    owner = vid[:vid.index(":")]
                    # Get the new url.
                    self.driver.get(
                        f"https://catalyst.library.jhu.edu/discovery/sourceRecord?vid={vid}&docId={doc}&recordOwner={owner}")

                    time.sleep(5)

                    # Get the relevant text from this new url.
                    pre = self.driver.find_element(By.TAG_NAME, 'pre')
                    # Format this text.
                    pre_text = pre.text.replace("\n", " ")
                    # The following code will run if there is no further need to continue.
                    # Because there is no metadata that can be retrieved.
                    # This doesn't necessarily mean that the relevant metadata doesn't exist on JHU.
                    # It is possible that it could be found manually through the previous tab.
                    # But as was mentioned before, that previous tab had web scraping limitations.
                    if "Record ID" and "was not found" in pre_text:
                        return {k.lower(): v for k, v in self.catalog_data.items()}

                    try:
                        index_of_ocn = pre_text.index("(OCoLC)")
                        self.catalog_data["OCN"] = pre_text[index_of_ocn + 7: pre_text.index(" ", index_of_ocn)]
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

                    indexes_of_fifty_part_one = find_occurrences_using_index(pre_text, "050 #4$a")
                    indexes_of_fifty_part_two = find_occurrences_using_index(pre_text, "050 00$a")
                    indexes_of_fifty_part_three = find_occurrences_using_index(pre_text, "050 14$a")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two + indexes_of_fifty_part_three

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = pre_text.index("$a", index_of_fifty)
                        index_of_second_potion = pre_text.index("$b", index_of_fifty)
                        index_of_intermediate_space = pre_text.index(" ", index_of_second_potion + 2)
                        index_of_final_space = pre_text.index(" ", index_of_intermediate_space + 1)
                        first_portion = pre_text[
                                        index_of_first_portion + 2: pre_text.index(" ", index_of_first_portion + 2)]
                        second_portion = pre_text[index_of_second_potion + 2: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = pre_text.index(" ", index_of_first_portion + 2)
                        if pre_text[index_of_filter_space + 1: index_of_filter_space + 3] != "$b":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("JHU")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

            elif input_type == "OCN":

                self.catalog_data["OCN"] = identifier

                self.driver.get(
                    f"https://catalyst.library.jhu.edu/discovery/search?query=lds10,contains,{identifier}&pfilter=rtype,exact,books&tab=Everything&search_scope=MyInst_and_CI&vid=01JHU_INST:JHU&offset=0")

                time.sleep(5)

                try:

                    title = self.driver.find_element(By.TAG_NAME, 'prm-highlight')
                    printable_title = title.text
                    link_to_book = self.driver.find_element(By.LINK_TEXT, printable_title)
                    link_to_book.click()

                    time.sleep(5)

                    # Unfortunately, the current url has limitations regarding its web scraping accommodations.
                    # Get the necessary information from the current url to access a new url.
                    url = self.driver.current_url
                    index_vid = url.index("vid")
                    index_doc = url.index("docid")
                    vid = url[index_vid + 4: url.index("&", index_vid)]
                    doc = url[index_doc + 6: url.index("&", index_doc)]
                    owner = vid[:vid.index(":")]
                    # Get the new url.
                    self.driver.get(
                        f"https://catalyst.library.jhu.edu/discovery/sourceRecord?vid={vid}&docId={doc}&recordOwner={owner}")

                    time.sleep(5)
                    # Get the relevant text from this new url.
                    pre = self.driver.find_element(By.TAG_NAME, 'pre')
                    # Format this text.
                    pre_text = pre.text.replace("\n", " ")
                    # The following code will run if there is no further need to continue.
                    # Because there is no metadata that can be retrieved.
                    # This doesn't necessarily mean that the relevant metadata doesn't exist on JHU.
                    # It is possible that it could be found manually through the previous tab.
                    # But as was mentioned before, that previous tab had web scraping limitations.
                    if "Record ID" and "was not found" in pre_text:
                        return self.send_dictionary()

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

                    indexes_of_isbn_twenty = find_occurrences_using_index(pre_text, "020 ##$a")
                    indexes_of_isbn_seven_seven_six = find_occurrences_using_index(pre_text, "776 ##$z")
                    indexes_of_isbn = indexes_of_isbn_twenty + indexes_of_isbn_seven_seven_six

                    for index_ISBN in indexes_of_isbn:
                        self.catalog_data["ISBN"].append(
                            pre_text[index_ISBN + 8: pre_text.index(" ", index_ISBN + 8)].replace("-", ""))

                    indexes_of_fifty_part_one = find_occurrences_using_index(pre_text, "050 #4$a")
                    indexes_of_fifty_part_two = find_occurrences_using_index(pre_text, "050 00$a")
                    indexes_of_fifty_part_three = find_occurrences_using_index(pre_text, "050 14$a")
                    indexes_of_fifty = indexes_of_fifty_part_one + indexes_of_fifty_part_two + indexes_of_fifty_part_three

                    for index_of_fifty in indexes_of_fifty:
                        index_of_first_portion = pre_text.index("$a", index_of_fifty)
                        index_of_second_potion = pre_text.index("$b", index_of_fifty)
                        index_of_intermediate_space = pre_text.index(" ", index_of_second_potion + 2)
                        index_of_final_space = pre_text.index(" ", index_of_intermediate_space + 1)
                        first_portion = pre_text[
                                        index_of_first_portion + 2: pre_text.index(" ", index_of_first_portion + 2)]
                        second_portion = pre_text[index_of_second_potion + 2: index_of_final_space]
                        # Determine whether to keep the second portion or not.
                        # Based on whether the second portion returns the information we are looking for.
                        index_of_filter_space = pre_text.index(" ", index_of_first_portion + 2)
                        if pre_text[index_of_filter_space + 1: index_of_filter_space + 3] != "$b":
                            lccn = first_portion
                        else:
                            lccn = first_portion + second_portion
                        self.catalog_data["LCCN"].append(lccn)
                        self.catalog_data["LCCN_Source"].append("JHU")

                    return self.send_dictionary()

                except NoSuchElementException:
                    return self.send_dictionary()

                except ValueError:
                    return self.send_dictionary()

        except WebDriverException:
            # print(f"Browser session has been closed or lost: {e}")
            self.driver = webdriver.Chrome()
            return {k.lower(): v for k, v in self.catalog_data.items()}
