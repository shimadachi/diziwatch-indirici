from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import os
import sys


class Webdriver:
    def __init__(self):
        self.driver = None

    def driver_start(self):
        if getattr(sys, "frozen", False):
            wd = sys._MEIPASS
        else:
            wd = os.getcwd()
        rp = wd + "/uBlock0_1.58.0.firefox.signed.xpi"
        options = webdriver.FirefoxOptions()

        options.add_argument("-headless")
        options.page_load_strategy = "eager"
        options.set_preference("permissions.default.image", 2)
        options.set_preference("media.volume_scale", "0.0")

        self.driver = webdriver.Firefox(options=options)
        self.driver.install_addon(rp)

    def driver_quit(self):
        try:
            self.driver.quit()
        except AttributeError:
            pass

    # 0 : default = wait located return element(s)
    # 1 : wait clickable return element(s)
    # 2 : wait clickable and located return element(s)
    def wait_and_find_element(
        self,
        by,
        element,
        wait_delay=10,
        max_attempt=3,
        wait_mode=0,
        elements_mode=False,
    ):

        attempt = 0
        wait_mode_element = lambda: WebDriverWait(self.driver, wait_delay).until(
            EC.presence_of_element_located((by, element))
        )
        wait_mode_clickable = lambda: WebDriverWait(self.driver, wait_delay).until(
            EC.element_to_be_clickable((by, element))
        )
        while attempt < max_attempt:
            try:
                if wait_mode == 0:
                    wait_mode_element()
                if wait_mode == 1:
                    wait_mode_clickable()
                if wait_mode == 2:
                    wait_mode_element()
                    wait_mode_clickable()
                if elements_mode == True:
                    return self.driver.find_elements(by, element)
                else:
                    return self.driver.find_element(by, element)
            except (
                selenium.common.exceptions.StaleElementReferenceException,
                selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                attempt += 1
                pass
