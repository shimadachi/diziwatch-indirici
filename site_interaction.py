from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import yt_dlp
from rich.progress import Progress
import re
import time
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy import get_style
###Webdriver


class Webdriver:
    def __init__(self):
        self.driver = None

    def driver_start(self):
    
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        options.page_load_strategy = "eager"
        options.set_preference("permissions.default.image", 2)
        options.set_preference("media.volume_scale", "0.0")


        self.driver = webdriver.Firefox(options=options)

    def driver_quit(self):
        try:
            self.driver.quit()
        except AttributeError:
            pass


    # 0 : default = wait located return element(s)
    # 1 : wait clickable return element(s)
    # 2 : wait clickable and located return element(s) 
    def wait_and_find_element(self, by, element,  default_wait_delay=10, max_attempt=3, wait_mode = 0,elements_mode = False ):


        attempt = 0
        while attempt < max_attempt:
            try:
                if wait_mode == 0:
                    WebDriverWait(self.driver, default_wait_delay).until(
                        EC.presence_of_element_located((by, element))
                    )
                    if elements_mode == True:
                        return self.driver.find_elements(by, element)
                    else:
                        return self.driver.find_element(by,element)
                if wait_mode == 1:
                    WebDriverWait(self.driver, default_wait_delay).until(
                        EC.element_to_be_clickable((by, element))
                    )
                    if elements_mode == True:
                        return self.driver.find_elements(by,element)
                    else:
                        return self.driver.find_element(by,element)
                if wait_mode == 2:
                    WebDriverWait(self.driver, default_wait_delay).until(EC.element_to_be_clickable((by, element)))
                    WebDriverWait(self.driver, default_wait_delay).until(EC.presence_of_element_located((by, element)))
                    if elements_mode == True:
                        return self.driver.find_elements(by,element)
                    else:
                        return self.driver.find_element(by,element)
            except (
                selenium.common.exceptions.StaleElementReferenceException,
                selenium.common.exceptions.ElementNotInteractableException,
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                attempt += 1
                pass


class Api(Webdriver):
    def __init__(self):
        super().__init__()
        self.selected_series = None
        self.filtered_text = None


    def go_site(self):
        self.driver.get("https://diziwatch.net/")

    def search(self):

        search_input = self.wait_and_find_element(By.CSS_SELECTOR, "#searchInput")
        search_input.clear()
        search_input.send_keys(input("Ara: ") + Keys.ENTER)

        list_series = []
        all_series = self.wait_and_find_element(By.XPATH, r"//*[@id='search-name']", default_wait_delay= 1, elements_mode= True)
        if all_series == None:
            raise ValueError
        for current_series in all_series:
            series = current_series.text
            list_series.append(series)
        if len(list_series) == 0:
            raise ValueError
        
        selected_series = inquirer.select(
            "Bulunan seriler: ", choices=list_series, qmark="-->", instruction= " ",
        ).execute()

        if selected_series == None:
            raise ValueError
        
        return selected_series

    # Istenen serinin sayfasina ulasir
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
                pass
            else:
                target_series = self.wait_and_find_element(
                By.XPATH, rf"//div[@id='search-name' and text()='{series}']", 1.5, 1,wait_mode=2)
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
                ###Secenek sun sectir
                season_opinion = inquirer.select(
                    "Sezonlar : ", choices=list(season_list.keys()),qmark="-->",instruction = " ",
                ).execute()
                season_list[season_opinion].click()

    # Serinin linklerini bir listeye atar ve return eder
    def get_episode_links(self):
        try:
            self.season_container()
        except (
            selenium.common.exceptions.NoSuchElementException,
            selenium.common.exceptions.TimeoutException,
        ):
            pass

        target_series_episodes_element = self.wait_and_find_element(
            By.XPATH, "//div[contains(@class, 'bolumust') and contains(@class, 'show')]",elements_mode=True
        )

        target_series_episode_dict = {}

        for episode in target_series_episodes_element:
            href_element = episode.find_element(By.XPATH, ".//a[@href]")
            href = href_element.get_attribute("href")
            target_series_episode_dict.update({href_element.text.replace("\n", "   "):  href })
        if not target_series_episode_dict == 1:
            target_series_episode_dict.update({"Butun bolumleri indir" : "all"})

        opinion = inquirer.select(message= "Bolumler: ", choices=target_series_episode_dict, multiselect=True).execute()


        target_series_episode_links = []

        for i in opinion:
            target_series_episode_links.append(target_series_episode_dict[i])

        all_links = target_series_episode_dict.values()

        if "all" in target_series_episode_links:
            return all_links
        else:
            return target_series_episode_links

class SeriesName:
    def __init__(self,driver,wait_and_find_element):
        self.driver = driver
        self.wait_and_find_element = wait_and_find_element
        self.series_name = None


    def filter_text(self, text):
        for i in ["?", ":"]:
            text = text.replace(i, "")
        return text

    # Anime ismine ulas!
    def get_series_name(self):
        series_name = self.wait_and_find_element(By.XPATH,"//h1[@class='title-border']").text
        return self.filter_text(series_name)


class Video:
    def __init__(self,driver,wait_and_find_element):
        self.driver = driver
        self.wait_and_find_element = wait_and_find_element
        self.series_name_handler = SeriesName(self.driver, self.wait_and_find_element)
        self.series_name = self.series_name_handler.get_series_name()

        
    # Kaliteyi ayarlar
    def set_quality_settings(self):

        video_player = self.wait_and_find_element(By.CSS_SELECTOR, "#player", wait_mode=1)
        video_player.click()

        setting_button = self.wait_and_find_element(By.CSS_SELECTOR, "div.jw-icon:nth-child(15)",wait_mode=1)
        setting_button.click()

        video_quality_info_element = self.wait_and_find_element(
            By.CSS_SELECTOR,
            "#jw-player-settings-submenu-quality > div:nth-child(1)",
            0.5,
            1,
            wait_mode=2
        )
        if video_quality_info_element:
            child_resolutions_elements = video_quality_info_element.find_elements(
                By.XPATH, "*",
            )
            resolutions = {}
            for child_resolutions_element in child_resolutions_elements:
                resolution = int(
                    child_resolutions_element.get_attribute("aria-label").replace("p", "")
                )
                resolutions.update({resolution: child_resolutions_element})
            sorted_resolutions = sorted(resolutions.items(), reverse=True)
            sorted_resolutions[0][1].click()

    

    def download_video(self, series_name, file_name, path= None):
        video_element = self.wait_and_find_element(By.CSS_SELECTOR, ".jw-video")
        src = video_element.get_attribute("src")
        self.driver.get("about:blank")
        yt_dlp.std_headers["Referer"] = "https://diziwatch.net/"
        URL = src
        ydl_opts = {
            "outtmpl": rf"{path}\{series_name}/{file_name}.%(ext)s",
            "ignoreerrors": True,
            "progress_hooks": [lambda d: self.ytdlp_hook(d)],
            "logger": Logger(),
        }
        with Progress() as self.progress:
            self.downloading = self.progress.add_task("[red]Indiriliyor", total=100,)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(URL)
            self.progress.remove_task(self.downloading)



    def download_episodes(self, target_series_episode_links,path= None):


        for site in target_series_episode_links:
            self.driver.get(site)

            file_name = self.series_name_handler.filter_text(self.wait_and_find_element(By.CSS_SELECTOR, "h1.title-border").text)

            try:
                self.set_quality_settings()
            except (
                selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.TimeoutException,
            ):
                pass

            self.download_video(self.series_name, file_name,path)

    def ytdlp_hook(self, d):
        if d["status"] == "downloading":
            percentage_raw = d["_percent_str"]
            percentage = float(re.search(rf"([0-9](?:[0-9]?).[0-9]%)", percentage_raw)[0].strip("%"))
            self.progress.update(self.downloading, completed=percentage)
        if d["status"] == "finished":
            print(f"Indirme Tamamlandi --> {d["filename"]}")


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
