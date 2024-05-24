from webdriver import Webdriver
from tools import InquirerSelect
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from rich.console import Console



class Api(Webdriver):
    def __init__(self):
        self.series_dict = None
        super().__init__()

    def go_site(self):
        self.driver.get(
            "https://diziwatch.net/wp-admin/admin-ajax.php?action=data_fetch"
        )

    def search(self) -> list:
        if not self.series_dict:
            with Console().status("[yellow] Arama listesi yükleniyor", spinner="point", spinner_style="white"):
                self.series_dict = {}

                search_elements = self.wait_and_find_element(
                    By.ID, "searchelement", elements_mode=True
                )
                for search_element in search_elements:
                    href = search_element.find_element(
                        By.XPATH, ".//div[@class='search-cat-img']/a"
                    ).get_attribute("href")
                    name = search_element.find_element(By.ID, "search-name").text
                    self.series_dict.update({name: href})

        series = InquirerSelect.inq(
            message="Arama: ", choices=self.series_dict.keys(), search=True, mandatory= False
        )
        series_link = self.series_dict.get(series)
        
        return series_link

    def go_series(self):
        series = self.search()
        self.driver.get(series)

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
                message="Sezonlar : ", choices=list(season_list.keys()), mandatory= False
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
            multiple_select=True,
            mandatory=False,
        )

        if not opinion:
            raise AssertionError

        target_series_episode_links = []

        for i in opinion:
            target_series_episode_links.append(target_series_episode_dict[i])

        return target_series_episode_links

    def get_series_name(self) -> str:
        series_name = self.wait_and_find_element(
            By.XPATH, "//h1[@class='title-border']"
        ).text
        return self.filter_text(series_name)
