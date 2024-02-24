def read_and_validate_file(filepath, file_type):
    """
    Reads a file and checks if it contains valid ISBNs or OCNs based on the selected file type.
    Args:
        filepath: Path of the file to read.
        file_type: Type of the file content ('ISBN' or 'OCN') as selected by the user.
    Returns:
        A list of extracted and validated items (ISBNs or OCNs).
    """
    valid_items = []

    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

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

def is_valid_isbn(isbn):
    # Placeholder for a real ISBN validation logic
    return len(isbn) in [10, 13] and isbn.isdigit()

def is_valid_ocn(ocn):
    # Placeholder for a real OCN validation logic
    return ocn.isdigit()
