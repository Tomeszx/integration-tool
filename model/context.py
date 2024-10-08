from selenium.webdriver.chrome.webdriver import WebDriver

from apiObjects.podio_api import Podio
from model.podio_tasks import PodioTask
from pageObjects.pams.add_new_market_page import AddMarketPage
from pageObjects.pams.create_market_page import CreateMarketPage
from pageObjects.pams.edit_market_page import EditMarketPage
from pageObjects.pams.location_info_page import LocationInfoPage


class Context:
    def __init__(self, driver: WebDriver, podio: Podio, task: PodioTask):
        self.task = task
        self.podio = podio
        self.driver = driver
        self.create_page = CreateMarketPage(self.driver)
        self.info_page = LocationInfoPage(self.driver)
        self.edit_page = EditMarketPage(self.driver)
        self.add_page = AddMarketPage(self.driver)
