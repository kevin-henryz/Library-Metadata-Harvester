import re

def verifyFileFormat(filepath, file_type):
    """
    Reads a file and checks if it contains valid ISBNs or OCNs based on the selected file type.
    Additionally, checks if the file content matches the selected file type.
    Args:
        filepath: Path of the file to read.
        file_type: Type of the file content ('ISBN' or 'OCN') as selected by the user.
    Returns:
        A list of extracted and validated items (ISBNs or OCNs).
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        
        # Determine the content type of the file based on its contents
        predicted_type = predict_file_content_type(lines)

        # If the predicted content type does not match the user's selection, return an error
        if predicted_type != file_type:
            print(f"Warning: The content of the file does not seem to match the selected type '{file_type}'.")
            return 'Invalid', []

        # Validate items based on the file type
        if file_type == 'ISBN':
            valid_items = [line.strip() for line in lines if is_valid_isbn(line.strip())]
        elif file_type == 'OCN':
            valid_items = [line.strip() for line in lines if is_valid_ocn(line.strip())]

        if not valid_items:
            return 'Invalid', []
        return file_type, valid_items

    except Exception as e:
        print(f"Error reading file: {e}")
        return 'Invalid', []

def predict_file_content_type(lines):
    """
    Predicts whether the lines are more likely to contain ISBNs or OCNs.
    Args:
        lines: The lines of text to analyze.
    Returns:
        A predicted content type ('ISBN' or 'OCN').
    """
    isbn_like, ocn_like = 0, 0
    for line in lines:
        clean_line = line.strip().replace('-', '').replace(' ', '')
        if len(clean_line) in [10, 13] and re.match(r'^\d{9}[\dX]$', clean_line) or re.match(r'^\d{13}$', clean_line):
            isbn_like += 1
        elif clean_line.isdigit():
            ocn_like += 1
    
    # More ISBN-like lines than OCN-like lines
    if isbn_like > ocn_like:
        return 'ISBN'
    # More OCN-like lines than ISBN-like lines, or equal but not zero
    elif ocn_like >= isbn_like and ocn_like > 0:
        return 'OCN'
    # Default or uncertain, could implement additional checks or return 'Unknown'
    return 'Unknown'


def is_valid_isbn(isbn):
    """
    Check if the ISBN is valid.
    Args:
        isbn: The ISBN to validate.
    Returns:
        True if the ISBN is valid, False otherwise.
    """
    isbn = isbn.replace('-', '').replace(' ', '')
    if len(isbn) == 10 and re.match(r'^\d{9}[\dX]$', isbn):
        return sum((10 - i) * (int(x) if x != 'X' else 10) for i, x in enumerate(isbn)) % 11 == 0
    elif len(isbn) == 13 and re.match(r'^\d{13}$', isbn):
        return sum((int(num) * (1 if idx % 2 == 0 else 3) for idx, num in enumerate(isbn))) % 10 == 0
    return False

def is_valid_ocn(ocn):
    """
    Check if the OCN is valid.
    Args:
        ocn: The OCN to validate.
    Returns:
        True if the OCN is valid, False otherwise.
    """
    return ocn.isdigit()