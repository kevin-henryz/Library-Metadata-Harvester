import unittest
import os
import sys


test_dir_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(test_dir_path, '..'))

src_dir = os.path.join(project_root, 'src')
sys.path.append(src_dir)

apis_dir = os.path.join(src_dir, 'apis')
webScrape_dir = os.path.join(src_dir, 'webScraping')
util_dir = os.path.join(src_dir, 'util')


sys.path.append(apis_dir)
sys.path.append(util_dir)
sys.path.append(webScrape_dir)

if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    # Construct the full path to the 'api' directory
    base_dir = os.path.dirname(__file__)  # Gets the directory of the current script
    api_dir = os.path.join(base_dir, 'api')  # Moves up one directory and into the 'api' directory
    test_suite = test_loader.discover(start_dir=api_dir, pattern='test*.py')
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
