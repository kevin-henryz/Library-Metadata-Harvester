import isbnlib
import re

output_dictionary = {
    'ISBN': [],
    'OCN': '',
    'LCCN': [],
    'LCCN_Source': []
}


def optimize_dictionary(input_dictionary):
    # Clean the ISBN, OCN, and LCCN fields in the input dictionary and return the cleaned fields in the output dictionary
    # Call this function in the API classes to clean the fields before returning the output dictionary

    # extract the fields from the input dictionary
    isbn_list = input_dictionary["ISBN"]
    ocn = input_dictionary["OCN"]
    lccn_list = input_dictionary["LCCN"]
    lccn_source_list = input_dictionary["LCCN_Source"]

    # clean the fields and store optimal output choice to the output dictionary
    output_dictionary["ISBN"] = best_clean_isbn(isbn_list) if isbn_list else []
    output_dictionary["OCN"] = clean_ocn(ocn) if ocn else ''
    output_dictionary["LCCN"] = best_clean_lccn(lccn_list) if lccn_list else []
    output_dictionary["LCCN_SOURCE"] = [lccn_source_list[0]] if output_dictionary["LCCN"] else []

    return output_dictionary


def best_clean_isbn(isbn_list):
    # Filter out invalid ISBNs and return the one with the highest ASCII sum
    clean_list = clean_isbn_list(isbn_list)
    best_isbn = get_highest_ascii_item(clean_list) if clean_list else []
    return best_isbn


def clean_isbn_list(isbn_list):
    # Remove non-digit characters from the beginning and end of each string and filter out invalid ISBNs
    isbn_list = [item for item in isbn_list if item.isdigit()]
    isbn_list = [item for item in isbn_list if isbnlib.is_isbn10(item) or isbnlib.is_isbn13(item)]
    return isbn_list if isbn_list else []


def get_highest_ascii_item(input_list):
    # Convert each string to an integer and then sum up their ASCII values, and return the highest valued one
    ascii_sums = [sum(ord(char) for char in str(int_val)) for int_val in input_list]
    max_index = ascii_sums.index(max(ascii_sums))
    return [input_list[max_index]] if input_list else []


def clean_ocn(ocn):
    # Remove non-digit characters from the beginning and end of the string and check the length, then return the cleaned OCN if valid
    stripped_ocn = re.sub(r'^\D+|\D+$', '', ocn)
    if bool(re.search(r'\D', stripped_ocn)) or len(stripped_ocn) < 8 or len(stripped_ocn) > 11:
        return ''
    return stripped_ocn


def best_clean_lccn(lccn_list):
    # Clean the LCCN list and return the longest string out of the valid options
    clean_lccn_list = clean_lccn(lccn_list)
    best_lccn = longest_string_in_list(clean_lccn_list) if clean_lccn_list else []
    return best_lccn


def clean_lccn(lccn_list):
    # Remove invalid LCCNs from the list, truncates hyphenated ones, and return the cleaned list of valid LCCNs
    cleaned_lccn_list = []
    pattern = r'^[A-Za-z]{1,3}[0-9A-Za-z. ]*$'
    for lccn in lccn_list:
        if '-' in lccn:
            lccn = lccn.split('-')[0]
        if len(lccn) <= 25 and re.match(pattern,
                                        lccn):  # Check if the length of the string is less than or equal to 20 characters
            cleaned_lccn_list.append(lccn)
    return cleaned_lccn_list if cleaned_lccn_list else []


def longest_string_in_list(input_list):
    # Find the longest string in the list and return it. This is used in choosing from the clean LCCN's
    if not input_list:
        return []
    longest = input_list[0]
    for string in input_list[1:]:
        if len(string) > len(longest):
            longest = string
    return [longest]  # Wrap the longest string in a list before returning it
