from webdriver import Webdriver
from termcolor import colored
from tools import InquirerSelect
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions

class Api(Webdriver):
    def __init__(self):
        super().__init__()

    def go_site(self): 
        self.driver.get("https://diziwatch.net/")

    def search(self) -> list:

        search_input = self.wait_and_find_element(By.CSS_SELECTOR, "#searchInput")
        search_input.clear()
        search_input.send_keys(input(colored("Ara: ", "light_cyan")) + Keys.ENTER)

        list_series = []
        all_series = self.wait_and_find_element(
            By.XPATH,
            r"//*[@id='search-name']",
            wait_delay=1,
            max_attempt=1,
            elements_mode=True,
        )
        if all_series == None:
            raise ValueError
        for current_series in all_series:
            series = current_series.text
            list_series.append(series)

        selected_series = InquirerSelect.inq(
            message="Bulunan seriler: ", choices=list_series
        )

        if selected_series == None:
            raise ValueError

        return selected_series

    def go_series(self):
        while True:
            try:
                series = self.search()
                if series == None:
                    raise ValueError
            except (
                selenium.common.exceptions.TimeoutException,
                selenium.common.exceptions.NoSuchElementException,
                ValueError,
            ):
                print(colored("Aradığınız anime/dizi bulunamadı", "red"))
                pass
            else:
                target_series = self.wait_and_find_element(
                    By.XPATH,
                    rf'//div[@id="search-name" and text()="{series}"]',
                    1.5,
                    1,
                    wait_mode=2,
                )
                target_series.click()
                break

    def season_container(self):

        season_list = {}

        season_check = self.wait_and_find_element(By.ID, "myBtnContainer")
        buttons = season_check.find_elements(By.TAG_NAME, "button")

        for button in buttons:
            season = button.get_attribute("search-text").strip()
            season_list.update({season: button})
        if len(season_list) == 1:
            pass
        else:
            season_opinion = InquirerSelect.inq(
                message="Sezonlar : ", choices=list(season_list.keys())
            )
            season_list[season_opinion].click()

    def get_episode_links(self) -> list:
        try:
            self.season_container()
        except (
            selenium.common.exceptions.NoSuchElementException,
            selenium.common.exceptions.TimeoutException,
        ):
            pass

        target_series_episodes_element = self.wait_and_find_element(
            By.XPATH,
            "//div[contains(@class, 'bolumust') and contains(@class, 'show')]",
            elements_mode=True,
        )

        target_series_episode_dict = {}

        for episode in target_series_episodes_element:
            href_element = episode.find_element(By.XPATH, ".//a[@href]")
            href = href_element.get_attribute("href")
            target_series_episode_dict.update(
                {href_element.text.replace("\n", "   "): href}
            )

        opinion = InquirerSelect.inq(
            message="Bölümler: ",
            choices=target_series_episode_dict,
            episode_select=True,
        )

        target_series_episode_links = []

        for i in opinion:
            target_series_episode_links.append(target_series_episode_dict[i])

        return target_series_episode_links
    
    def get_series_name(self) -> str:
        series_name = self.wait_and_find_element(
            By.XPATH, "//h1[@class='title-border']"
        ).text
        return self.filter_text(series_name)