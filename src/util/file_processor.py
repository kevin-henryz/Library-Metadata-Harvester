# file_processor.py

def read_and_validate_file(filepath):
    """
    Reads a file and checks if it contains ISBNs or OCNs.
    Returns a tuple: (file_type, data)
    where file_type is either 'ISBN', 'OCN', or 'Invalid', and data is a list of extracted items.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

        if all(is_valid_isbn(line.strip()) for line in lines):
            return ('ISBN', [line.strip() for line in lines])
        elif all(is_valid_ocn(line.strip()) for line in lines):
            return ('OCN', [line.strip() for line in lines])
        else:
            return ('Invalid', [])
    except Exception as e:
        print(f"Error reading file: {e}")
        return ('Invalid', [])

def is_valid_isbn(isbn):
    """
    Validates if a string is a valid ISBN. Implementation needs to be checked
    """
    # Simple example: check length
    return len(isbn) in [10, 13]

def is_valid_ocn(ocn):
    """
    Validates if a string is a valid OCN. Implementation needs to be checked
    """
    # Simple example: check if it's numeric
    return ocn.isdigit()
