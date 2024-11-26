from tools import NameHandler
from selenium.webdriver.common.by import By
import yt_dlp
import re
from termcolor import colored
import selenium.common.exceptions
from rich.progress import Progress
from os import name
import time


class Video:
    def __init__(self, driver):
        self.driver = driver.driver
        self.wait_and_find_element = driver.wait_and_find_element
        self.name_handler = NameHandler()
        self.series_name = self.name_handler.get_series_name(self.wait_and_find_element)

    def set_quality_settings(self):

        time.sleep(1)
        video_player = self.wait_and_find_element(
            By.CSS_SELECTOR,
            "#player",
            wait_mode=2,
            wait_delay=0.5,
            max_attempt=1,
        ).click()

        setting_button = self.wait_and_find_element(
            By.CSS_SELECTOR,
            "div.jw-icon:nth-child(15)",
            wait_mode=1,
            wait_delay=0.5,
            max_attempt=1,
        ).click()

        video_quality_info_element = self.wait_and_find_element(
            By.CSS_SELECTOR,
            "#jw-player-settings-submenu-quality > div:nth-child(1)",
            wait_delay=0.5,
            max_attempt=1,
            wait_mode=2,
        )
        if video_quality_info_element:
            child_resolutions_elements = video_quality_info_element.find_elements(
                By.XPATH,
                "*",
            )
            resolutions = {}
            for child_resolutions_element in child_resolutions_elements:
                resolution = int(
                    child_resolutions_element.get_attribute("aria-label").replace(
                        "p", ""
                    )
                )
                resolutions.update({resolution: child_resolutions_element})
            sorted_resolutions = sorted(resolutions.items(), reverse=True)
            sorted_resolutions[0][1].click()

    def download_video(self, series_name, file_name, path=None):

        match name:
            case "nt":
                outmpl = rf"{path}\{series_name}/{file_name}.%(ext)s"
            case "posix":
                outmpl = rf"{path}/{series_name}/{file_name}.%(ext)s"

        video_element = self.wait_and_find_element(By.CSS_SELECTOR, ".jw-video")
        src = video_element.get_attribute("src")

        self.driver.get("about:blank")
        yt_dlp.std_headers["Referer"] = "https://diziwatch.net/"
        URL = src
        ydl_opts = {
            "outtmpl": outmpl,
            "ignoreerrors": True,
            "progress_hooks": [lambda d: self.ytdlp_hook(d)],
            "logger": Yt_Logger(),
            "concurrent_fragment_downloads": 2,
        }
        with Progress() as self.progress:
            self.downloading = self.progress.add_task(
                "[red]İndiriliyor",
                total=100,
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(URL)
            self.progress.remove_task(self.downloading)

    def download_episodes(
        self, target_series_episode_links, path=None, re_naming="Kapali"
    ):

        for site in target_series_episode_links:
            while True:
                try:
                    self.driver.get(site)

                    file_name = self.name_handler.filter_text(
                        self.wait_and_find_element(
                            By.CSS_SELECTOR, "h1.title-border"
                        ).text
                    )

                    if re_naming == "Acik":
                        file_name = self.name_handler.re_naming(file_name)

                    try:
                        self.set_quality_settings()
                    except (
                        selenium.common.exceptions.NoSuchElementException,
                        selenium.common.exceptions.TimeoutException,
                    ):
                        pass

                    self.download_video(self.series_name, file_name, path)
                except (selenium.common.StaleElementReferenceException, AttributeError):
                    pass
                else:
                    break

    def ytdlp_hook(self, d):
        if d["status"] == "downloading":
            percentage_raw = d["_percent_str"]
            percentage = float(
                re.search(rf"([0-9](?:[0-9]?).[0-9]%)", percentage_raw)[0].strip("%")
            )
            self.progress.update(self.downloading, completed=percentage)
        if d["status"] == "finished":
            print(colored(f'İndirme Tamamlandı --> {d["filename"]}', "light_green"))


class Yt_Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
