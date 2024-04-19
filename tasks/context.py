from selenium.webdriver.chrome.webdriver import WebDriver

from api_objects.podio_api import Podio
from page_objects.shop_management.add_new_location_page import AddLocationPage
from page_objects.shop_management.create_location_page import CreateLocationPage
from page_objects.shop_management.edit_location_page import EditLocationPage
from page_objects.shop_management.location_info_page import LocationInfoPage


class Context:
    def __init__(self, driver: WebDriver, podio: Podio, task: dict):
        self.task = task
        self.podio = podio
        self.podio_data = self.podio.get_partner_details(task['shop_item_id'])
        self.driver = driver
        self.create_page = CreateLocationPage(self.driver, self.podio_data)
        self.info_page = LocationInfoPage(self.driver, self.podio_data)
        self.edit_page = EditLocationPage(self.driver, self.podio_data)
        self.add_page = AddLocationPage(self.driver, self.podio_data)
