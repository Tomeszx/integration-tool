import os

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from tasks.logic import TasksManager
from interface import GUI


def get_selected_tasks(user_inputs: dict, chosen_tasks: dict):
    if user_inputs['All_tasks']:
        return {
            task_key.replace("_", " "): chosen_tasks[task_key.replace("_", " ")]
            for task_key, value in user_inputs.items()
            if task_key.replace("_", " ") in chosen_tasks and value
        }
    return chosen_tasks


def setup_chromedriver_options(user_inputs: dict) -> ChromeOptions:
    chrome_options = ChromeOptions()

    if not user_inputs["headless_website"]:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.page_load_strategy = "eager"

    prefs = {"profile.default_content_settings.popups": 2, "download.default_directory": os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


def run():
    gui = GUI()
    user_inputs = gui.handle()
    chosen_tasks = get_selected_tasks(user_inputs, chosen_tasks=gui.tasks)

    options = setup_chromedriver_options(user_inputs)
    driver = Chrome(options=options, service=ChromeService())

    manager = TasksManager(user_inputs['comment_frequency'], user_inputs, options, driver)
    manager.run(chosen_tasks)


if __name__ == "__main__":
    run()
