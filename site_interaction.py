from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import yt_dlp
import time
import questionary
from rich.progress import Progress
import re

###Webdriver


class Api:
    def __init__(self):

        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        options.page_load_strategy = "eager"
        options.set_preference("permissions.default.image", 2)
        options.set_preference("media.volume_scale", "0.0")
        # options.set_preference("javascript.enabled", False)
        # options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        self.driver = webdriver.Firefox(options=options)

    def driver_quit(self):

        self.driver.quit()

    def wait_element(self, by, element, default_wait_delay=10, max_attempt=3):

        attempt = 0
        while attempt < max_attempt:
            try:
                WebDriverWait(self.driver, default_wait_delay).until(
                    EC.presence_of_element_located((by, element))
                )
                break
            except (
                selenium.common.exceptions.StaleElementReferenceException,
                selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                attempt += 1
                pass

    def wait_element_clickable(self, by, element, default_wait_delay=10, max_attempt=3):

        attempt = 0
        while attempt < max_attempt:
            try:
                WebDriverWait(self.driver, default_wait_delay).until(
                    EC.element_to_be_clickable((by, element))
                )
                break
            except (
                selenium.common.exceptions.StaleElementReferenceException,
                selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                attempt += 1
                pass

    def go_site(self):
        self.driver.get("https://diziwatch.net/")

    def search(self):
        self.wait_element(By.CSS_SELECTOR, "#searchInput")
        search_input = self.driver.find_element(By.CSS_SELECTOR, "#searchInput")
        search_input.clear()
        search_input.send_keys(input("Search: ") + Keys.ENTER)

        list_series = []
        self.wait_element(By.XPATH, r"//*[@id='search-name']", 1)
        all_series = self.driver.find_elements(By.XPATH, r"//*[@id='search-name']")
        for current_series in all_series:
            series = current_series.text
            list_series.append(series)
        if len(list_series) == 0:
            raise ValueError
        return questionary.select(
            "Bulunan seriler: ", choices=list_series, qmark=""
        ).ask()

    # Istenen serinin sayfasina ulasir
    def go_series(self):

        # self.wait_element(By.CSS_SELECTOR, "#searchInput")
        # search_input = self.driver.find_element(By.CSS_SELECTOR, "#searchInput")
        # search_input.clear()

        # attempt = 0

        while True:
            try:
                series = self.search()

                self.wait_element(
                    By.XPATH, rf"//div[@id='search-name' and text()='{series}']", 1.5, 1
                )
                self.wait_element_clickable(
                    By.XPATH, rf"//div[@id='search-name' and text()='{series}']", 1.5, 1
                )
                target_series = self.driver.find_element(
                    By.XPATH, rf"//div[@id='search-name' and text()='{series}']"
                )
                target_series.click()
                break
            except (
                selenium.common.exceptions.TimeoutException,
                selenium.common.exceptions.NoSuchElementException,
                ValueError,
            ):
                # attempt += 1
                pass

    # Serinin linklerini bir listeye atar ve return eder
    def get_episode_links(self):
        try:
            self.season_container()
        except (
            selenium.common.exceptions.NoSuchElementException,
            selenium.common.exceptions.TimeoutException,
        ):
            pass

        self.wait_element(
            By.XPATH, "//div[contains(@class, 'bolumust') and contains(@class, 'show')]"
        )
        target_series_episodes = self.driver.find_elements(
            By.XPATH, "//div[contains(@class, 'bolumust') and contains(@class, 'show')]"
        )

        target_series_episode_links = []

        for episode in target_series_episodes:
            href_element = episode.find_element(By.XPATH, ".//a[@href]")
            href = href_element.get_attribute("href")
            target_series_episode_links.append(href)

        return target_series_episode_links

    def filter_text(self, text):
        for i in ["?", ":"]:
            text = text.replace(i, "")
        return text

    # Anime ismine ulas!
    def get_series_name(self):
        series_name = self.driver.find_element(
            By.XPATH, "//h1[@class='title-border']"
        ).text
        return self.filter_text(series_name)

    def download_series(self, target_series_episode_links):

        series_name = self.get_series_name()

        for site in target_series_episode_links:
            self.driver.get(site)

            self.wait_element(By.CSS_SELECTOR, "h1.title-border")

            file_name = self.filter_text(
                self.driver.find_element(By.CSS_SELECTOR, "h1.title-border").text
            )

            try:
                self.set_quality_settings()
            except (
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                pass

            self.download_video(series_name, file_name)

    # Kaliteyi ayarlar
    def set_quality_settings(self):

        self.wait_element_clickable(By.CSS_SELECTOR, "#player")

        video_player = self.driver.find_element(By.CSS_SELECTOR, "#player")
        video_player.click()

        self.wait_element_clickable(By.CSS_SELECTOR, "div.jw-icon:nth-child(15)")
        setting_button = self.driver.find_element(
            By.CSS_SELECTOR, "div.jw-icon:nth-child(15)"
        )
        setting_button.click()

        self.wait_element(
            By.CSS_SELECTOR,
            "#jw-player-settings-submenu-quality > div:nth-child(1)",
            0.5,
            1,
        )

        self.wait_element_clickable(
            By.CSS_SELECTOR,
            "#jw-player-settings-submenu-quality > div:nth-child(1)",
            0.5,
            1,
        )
        video_quality_info_element = self.driver.find_element(
            By.CSS_SELECTOR,
            "#jw-player-settings-submenu-quality > div:nth-child(1)",
        )

        child_resolutions_elements = video_quality_info_element.find_elements(
            By.XPATH, "*"
        )
        resolutions = {}
        for child_resolutions_element in child_resolutions_elements:
            resolution = int(
                child_resolutions_element.get_attribute("aria-label").replace("p", "")
            )
            resolutions.update({resolution: child_resolutions_element})
        sorted_resolutions = sorted(resolutions.items(), reverse=True)
        sorted_resolutions[0][1].click()

    def season_container(self):
        season_list = {}

        self.wait_element(By.ID, "myBtnContainer")
        season_check = self.driver.find_element(By.ID, "myBtnContainer")
        buttons = season_check.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            season = button.get_attribute("search-text").strip()
            season_list.update({season: button})
        if len(season_list) == 1:
            pass
        else:
            ###Secenek sun sectir
            season_opinion = questionary.select(
                "Sezonlar : ", choices=list(season_list.keys())
            ).ask()
            season_list[season_opinion].click()

    def download_video(self, series_name, file_name, path=r"D:\emby_video"):
        self.wait_element(By.CSS_SELECTOR, ".jw-video")
        video_element = self.driver.find_element(By.CSS_SELECTOR, ".jw-video")
        src = video_element.get_attribute("src")
        self.driver.get("about:blank")
        yt_dlp.std_headers["Referer"] = "https://diziwatch.net/"
        URLS = src
        ydl_opts = {
            "outtmpl": rf"{path}\{series_name}/{file_name}.%(ext)s",
            "ignoreerrors": True,
            "progress_hooks": [lambda d: self.yt_hook(d)],
            "logger": Logger(),
        }
        with Progress() as self.progress:
            self.downloading = self.progress.add_task("[red]Indiriliyor", total=100)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(URLS)
            self.progress.remove_task(self.downloading)

    # with Progress() as progress:
    #     downloading = progress.add_task("[red]Downloading", total=100)

    def yt_hook(self, d):
        if d["status"] == "downloading":
            percentage_raw = d["_percent_str"]
            percentage = float(re.search(rf"([0-9](?:[0-9]?).[0-9]%)", percentage_raw)[0].strip("%"))
            self.progress.update(self.downloading, completed=percentage)
        if d["status"] == "finished":
            print(f"Completed --> {d["filename"]}")


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
