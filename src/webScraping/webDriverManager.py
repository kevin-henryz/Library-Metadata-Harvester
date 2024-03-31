from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import logging

class WebDriverManager:
    _instance = None

    @classmethod
    def get_driver(cls):
        if cls._instance is None:
            try:
                cls._initialize_driver()
            except Exception as e:
                logging.error("Could not initialize WebDriver. Is Google Chrome installed?")
                raise RuntimeError("Google Chrome must be installed to use this application.") from e
        return cls._instance

    @classmethod
    def _initialize_driver(cls):
        """Initialize a new WebDriver instance."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        cls._instance = webdriver.Chrome(options=options)

    @classmethod
    def close_driver(cls):
        """Close the current WebDriver instance."""
        if cls._instance:
            cls._instance.quit()
            cls._instance = None

    @classmethod
    def restart_driver(cls):
        """Restart the WebDriver instance."""
        cls.close_driver()
        cls._initialize_driver()